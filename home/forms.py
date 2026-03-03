from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        # tags_input is a custom form field (not a model field), so it must NOT be in fields
        fields = ['title', 'content', 'image']
        exclude = ['tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Enter your post title...',
                'style': (
                    'width:100%; padding:12px; border:1px solid #3b2f2f; '
                    'border-radius:6px; font-family:Georgia, serif; margin-bottom:15px; background-color:#fdfaf3;'
                )
            }),
            'content': forms.Textarea(attrs={
                'placeholder': "What's on your mind?",
                'rows': 6,
                'style': 'width:100%; padding:12px; border:1px solid #3b2f2f; border-radius:6px; font-family:Roboto, sans-serif; resize:vertical; margin-bottom:15px; background-color:#fdfaf3;'
            }),
            'tags_input': forms.TextInput(attrs={
                'placeholder': 'Tags (comma separated)...',
                'style': 'width:100%; padding:12px; border:1px solid #3b2f2f; border-radius:6px; margin-bottom:15px; background-color:#fdfaf3;'
            })
        }

    tags_input = forms.CharField(max_length=200, required=False)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self._save_tags(instance)
        return instance

    def _save_tags(self, instance):
        from .models import Tag
        tags_str = self.cleaned_data.get('tags_input', '')
        instance.tags.clear()
        if tags_str:
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            for name in tag_names:
                tag, created = Tag.objects.get_or_create(name=name)
                instance.tags.add(tag)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your comment here...'
            })
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'instagram_link', 'twitter_link', 'linkedin_link']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }
