from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = (
            "author",
        )
        widgets = {
            "pub_date": forms.DateTimeInput(
                format='%Y-%m-%d %H:%M:%S',
                attrs={"type": "datetime"},
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
