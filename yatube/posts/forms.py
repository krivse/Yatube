from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text',
                  'group',
                  'image',
                  )
        labels = {
            'image': ('Картинка'),
        }

    def clean_text(self):

        text = self.cleaned_data['text']
        if text == '':
            raise forms.ValidationError(
                'Поле "Текст" не может быть пустым'
            )
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
