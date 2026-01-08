from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.db.models import Count, Q
from django.utils.text import Truncator
from django.core.paginator import Paginator

from .models import Post, Comment, PostImage, Follow, Bookmark, Notification
from .forms import PostForm, CommentForm, SignUpForm, ProfileForm, UserUpdateForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login


def index(request):
    """
    Display all posts with pagination.
    Each post shows a truncated preview if content is long.
    """
    query = request.GET.get('q')
    if query:
        post_list = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        ).annotate(comment_count=Count('comments')).order_by('-created_at')
    else:
        post_list = Post.objects.annotate(comment_count=Count('comments')).order_by('-created_at')

    # Add bookmark status for authenticated users
    if request.user.is_authenticated:
        user_bookmarks = set(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
        for post in post_list:
            post.is_bookmarked = post.id in user_bookmarks

    paginator = Paginator(post_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Get trending tags for sidebar
    from .models import Tag
    trending_tags = Tag.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:10]

    return render(request, "home/index.html", {
        "page_obj": page_obj,
        "trending_tags": trending_tags
    })


@login_required
def add_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            gallery_images = request.FILES.getlist('images')
            for img in gallery_images:
                PostImage.objects.create(post=post, image=img)

            messages.success(request, "Post added successfully!")
            return redirect('index')
        else:
            messages.error(request, "There was an error with your submission.")
    else:
        form = PostForm()

    return render(request, 'home/add_post.html', {'form': form})


def login_view(request):

    """
    User login view using Django's AuthenticationForm.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(request.GET.get('next', 'index'))
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'home/login.html', {'form': form})


def signup_view(request):
    """
    User signup view using Custom SignUpForm.
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SignUpForm()

    return render(request, 'home/signup.html', {'form': form})


def logout_view(request):
    """
    Logout the user and redirect to home.
    """
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('index')


@login_required
def profile_view(request):
    """
    Show profile page with user's posts and allow profile editing.
    """
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        # Ensure profile exists, though signal should handle it
        if not hasattr(request.user, 'profile'):
            from .models import Profile
            Profile.objects.create(user=request.user)
            
        p_form = ProfileForm(instance=request.user.profile)

    user_posts = Post.objects.filter(author=request.user).order_by('-created_at')
    
    return render(request, 'home/profile.html', {
        'profile_user': request.user,
        'u_form': u_form,
        'p_form': p_form,
        'user_posts': user_posts
    })


@login_required
def delete_post(request, pk):
    """
    Delete a post if the current user is the author.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.author:
        post.delete()
        messages.success(request, 'Post deleted successfully!')
    else:
        messages.error(request, "You don't have permission to delete this post.")

    return redirect('index')


@login_required
def like_post(request, pk):
    """
    Toggle like/unlike for a post.
    """
    post = get_object_or_404(Post, pk=pk)
    liked = False
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        # messages.success(request, 'Post unliked.')
    else:
        post.likes.add(request.user)
        liked = True
        # Create notification for post author
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post
            )
        # messages.success(request, 'Post liked!')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'total_likes': post.total_likes()})

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def post_detail(request, pk):
    """
    Show post details with comments and gallery images.
    Allows adding a comment.
    """
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    images = post.images.all() 

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()

    # Check if post is bookmarked by current user
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()

    return render(request, 'home/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'images': images,
        'is_bookmarked': is_bookmarked
    })


@login_required
def add_comment(request, pk):
    """
    Add a comment to a post.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            # Create notification for post author
            if post.author != request.user:
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment
                )
            messages.success(request, 'Comment added successfully!')
        else:
            messages.error(request, 'Invalid comment submission.')

    return redirect('post_detail', pk=post.pk)


@login_required
def delete_comment(request, pk):
    """
    Delete a comment if the user is either the comment author or post author.
    """
    comment = get_object_or_404(Comment, pk=pk)
    post = comment.post

    if request.user == comment.author or request.user == post.author:
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
    else:
        messages.error(request, "You don't have permission to delete this comment.")

    return redirect('post_detail', pk=post.pk)


def public_profile(request, username):
    """
    Show a public profile for any user.
    """
    profile_user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    
    return render(request, 'home/profile.html', {
        'profile_user': profile_user,
        'user_posts': user_posts,
        'is_following': is_following,
    })


@login_required
def follow_user(request, username):
    """
    Toggle follow status for a user.
    """
    user_to_follow = get_object_or_404(User, username=username)
    
    if user_to_follow != request.user:
        follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        if not created:
            follow.delete()
            messages.success(request, f"Unfollowed {user_to_follow.username}.")
        else:
            # Create notification for new follower
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow'
            )
            messages.success(request, f"You are now following {user_to_follow.username}!")
            
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        is_following = Follow.objects.filter(follower=request.user, following=user_to_follow).exists()
        return JsonResponse({
            'is_following': is_following,
            'followers_count': user_to_follow.followers.count()
        })

    return redirect('public_profile', username=username)


@login_required
def bookmark_post(request, pk):
    """
    Toggle bookmark status for a post.
    """
    post = get_object_or_404(Post, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        bookmark.delete()
        bookmarked = False
        messages.success(request, 'Bookmark removed.')
    else:
        bookmarked = True
        messages.success(request, 'Post bookmarked!')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'bookmarked': bookmarked})
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def bookmarks_list(request):
    """
    Display all bookmarked posts for the current user.
    """
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('post', 'post__author')
    return render(request, 'home/bookmarks.html', {'bookmarks': bookmarks})


@login_required
def notifications_list(request):
    """
    Display all notifications for the current user.
    """
    notifications = request.user.notifications.select_related('sender', 'post')[:50]
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    return render(request, 'home/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })


@login_required
def mark_notification_read(request, pk):
    """
    Mark a notification as read.
    """
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications')


def trending_posts(request):
    """
    Display trending posts based on recent activity (likes + comments).
    """
    from datetime import timedelta
    from django.utils import timezone
    
    # Posts from last 7 days with most engagement
    week_ago = timezone.now() - timedelta(days=7)
    posts = Post.objects.filter(created_at__gte=week_ago).annotate(
        like_count=Count('likes'),
        comment_count=Count('comments')
    ).order_by('-like_count', '-comment_count')[:20]
    
    return render(request, 'home/trending.html', {'posts': posts})


def search_enhanced(request):
    """
    Enhanced search with filters for tags, authors, and content.
    """
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')  # all, tags, authors, posts
    
    results = []
    
    if query:
        if search_type == 'all' or search_type == 'posts':
            posts = Post.objects.filter(
                Q(title__icontains=query) | Q(content__icontains=query)
            ).select_related('author')
            results.extend(posts)
        
        if search_type == 'all' or search_type == 'tags':
            from .models import Tag
            tags = Tag.objects.filter(name__icontains=query)
            for tag in tags:
                results.extend(tag.posts.all())
        
        if search_type == 'all' or search_type == 'authors':
            authors = User.objects.filter(username__icontains=query)
            for author in authors:
                results.extend(author.posts.all())
    
    # Remove duplicates and paginate
    unique_posts = list(set(results))
    paginator = Paginator(unique_posts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'home/search_results.html', {
        'page_obj': page_obj,
        'search_query': query,
        'search_type': search_type
    })
