from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Tags (comma separated)...',
            'class': 'form-control'
        })
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'image']

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content or content == '<p><br></p>':
            raise forms.ValidationError("Content cannot be empty.")
        return content

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
                tag, _ = Tag.objects.get_or_create(name=name)
                instance.tags.add(tag)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'instagram_link', 'twitter_link', 'linkedin_link']