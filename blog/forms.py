from django import forms
from .models import Blog, BlogType
from ckeditor_uploader.widgets import CKEditorUploadingWidget


class BlogTypeForm(forms.ModelForm):
    class Meta:
        model = BlogType
        fields = {'type_name'}
        labels = {'type_name': ''}


class BlogForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget(), label='详情', required=True)
    class Meta:
        model = Blog
        fields = "__all__"
        # widgets = {'content': forms.Textarea(attrs={'cols': 80})}
