from django import forms
from .models import Article, Tag, Comment

class ArticleForm(forms.ModelForm):
    tags = forms.CharField(widget=forms.TextInput)
    class Meta:
        model = Article
        fields = ("title", "description", "content", "cover_image", "tags")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Article Title'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Write a short description'})
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Write your article (in markdown)'})
        self.fields['cover_image'].widget.attrs.update({'placeholder': 'Image'})
        self.fields['tags'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Comma seperated Tags'})

        for field in self.fields:
            self.fields[field].label = ""
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
        self.fields['body'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Write your comment'})
        self.fields['body'].label = ""


class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control", "placeholder":"Search articles"}), label="", )