from django.contrib.auth.forms import forms
from . models import *
from django_summernote.widgets import SummernoteWidget

class CreatePostForm(forms.ModelForm):
    body = forms.CharField(widget=SummernoteWidget()) 
    class Meta:
        model = Post
        fields = ('title', 'image', 'category', 'language', 'tags','list', 'description', 'body', 'is_public',)



class BookForm(forms.ModelForm):
    file = forms.FileField()
    class Meta:
        model = Book
        fields = ('name', 'author', 'category', 'tags', 'language', 'file', 'image', 'description')



class CreateContact(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('__all__')

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscribe
        fields = ('email', )

class FormCreatePage(forms.ModelForm):
    body = forms.CharField(widget=SummernoteWidget()) 
    class Meta:
        model = Page
        fields = ('title', 'body')

class FromPostCategory(forms.ModelForm):
    class Meta:
        model = PostCategory
        fields = ('name', 'language')


class FormBookCategory(forms.ModelForm):
    class Meta:
        model = BookCategory
        fields = ('name', 'language')


class PostSearchForm(forms.Form):
    q = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].label = 'Search For'
        self.fields['q'].widget.attrs.update(
            {'class': 'form-control'})
       




# Video

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'image', 'tags', 'language', 'list','category', 'description', ]

class VideoListForm(forms.ModelForm):
    class Meta:
        model = VideoList
        fields = ['name', 'image', 'tags', 'language','category', 'description', ]

class QualityForm(forms.ModelForm):
    class Meta:
        model = Quality
        fields = ['quality','file']



class VideoCommentForm(forms.ModelForm):
    class Meta:
        model = VideoComment
        fields = ['body']