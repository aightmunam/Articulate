from django import forms
from .models import Article, Tag, Comment

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("title", "description", "content", "cover_image", "tags")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control'})
        self.fields['cover_image'].widget.attrs.update({'class': 'form-control'})
        self.fields['tags'].widget.attrs.update({'class': 'form-control'})
        # self.fields['author'].widget.attrs.update({'class': 'form-control'})

    def clean_data(self):
        title = self.cleaned_data.get("title")
        if len(title) > 100:
            raise forms.ValidationError("This title is too long")
        description = self.cleaned_data.get("description")
        if len(description) > 350:
            raise forms.ValidationError("This description is too long")
        return self.cleaned_data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body'].widget.attrs.update({'class': 'form-control'})