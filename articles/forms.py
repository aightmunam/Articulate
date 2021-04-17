"""
Forms for the articles app
"""
from django import forms
from django.db.models import Q

from .models import Article, Comment, Tag


class ArticleForm(forms.ModelForm):
    """
    ModelForm for Article
    """
    tags = forms.CharField(widget=forms.TextInput)

    class Meta:
        model = Article
        fields = ('title', 'description', 'content', 'cover_image', 'tags')

    def __init__(self, *args, **kwargs):
        """
        Add request object to self, and add some styling for the form objects
        """
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Article Title'})
        self.fields['description'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Write a short description'})
        self.fields['content'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Write your article (in markdown)'})
        self.fields['cover_image'].widget.attrs.update({'placeholder': 'Image'})
        self.fields['tags'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Comma seperated Tags'})

        for field in self.fields:
            self.fields[field].label = ''

    def clean_title(self):
        """
        Validate title length
        """
        title = self.cleaned_data.get('title')
        if len(title) > 100:
            raise forms.ValidationError('The title is too long')
        return title

    def clean_description(self):
        """
        Validate description length
        """
        description = self.cleaned_data.get('description')
        if len(description) > 350:
            raise forms.ValidationError('The description is too long')
        return description

    def clean_tags(self):
        """
        Check if no empty strings are being sent as a tag
        """
        tags = self.cleaned_data['tags']
        tag_names = tags.split(',')
        for tag_name in tag_names:
            if not tag_name.strip():
                raise forms.ValidationError('The tags must be non-empty and separated by commas')

        return tags

    def save(self, commit=True):
        """
        Override save method to convert all the tag name strings into Tag objects and add it to m2m field with the
        current object
        """
        instance = super().save(commit=False)
        if commit:
            instance.author = self.request.user
            instance.save()

        tags = self.cleaned_data['tags']
        tag_names = [tag.strip().lower() for tag in tags.split(',') if tag and tag.strip()]

        for tag_name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            if not instance.tags.filter(name=tag.name).exists():
                instance.tags.add(tag)

        instance.tags.remove(*instance.tags.filter(~Q(name__in=tag_names)))

        return instance


class CommentForm(forms.ModelForm):
    """
    ModelForm for Comment
    """

    class Meta:
        model = Comment
        fields = ('body',)

    def __init__(self, *args, **kwargs):
        """
        Add request object to self, and add some styling for the form objects
        """
        self.request = kwargs.pop('request', None)
        self.article = kwargs.pop('article', None)
        print("in form comment", self.request, self.article)
        super().__init__(*args, **kwargs)

        self.fields['body'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Write your comment', 'style': 'height: 6em;'})
        self.fields['body'].label = ''

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.article = self.article
            instance.author = self.request.user
            instance.save()


class SearchForm(forms.Form):
    """
    Form for searching
    """
    query = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search articles, profiles and more...'}),
        label='',
    )
