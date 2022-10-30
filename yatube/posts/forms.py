from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('group', 'text')
        labels = {
            'group': 'Группа',
            'text': 'Текст поста'
        }
        help_texts = {
            'group': 'Группа в которой будет'
                     'опубликован пост',
            'text': 'пост не может быть пустым'
        }
