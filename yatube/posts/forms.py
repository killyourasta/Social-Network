from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        context = {
            'group': 'Группа',
            'text': 'Текст поста',
            'image': 'Картинка',
        }
        fields = ('group', 'text', 'image')
        widget = {
            'text': forms.Textarea(attrs={'cols': 40, 'rows': 10})
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
