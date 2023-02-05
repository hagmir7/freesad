from django.contrib.auth.forms import forms
from . models import *
from django_summernote.widgets import SummernoteWidget

class CreatePostForm(forms.ModelForm):
    body = forms.CharField(widget=SummernoteWidget()) 
    class Meta:
        model = Post
        fields = ('title', 'image', 'category', 'language', 'tags','list', 'description', 'body', 'is_public',)



class FormCreateBook(forms.ModelForm):
    body = forms.CharField(widget=SummernoteWidget()) 
    file = forms.FileField()
    class Meta:
        model = Book
        fields = ('name', 'author', 'category', 'language', 'pages', 'file', 'image', 'description', 'body', 'tags')



class CreateTemplateImage(forms.ModelForm):
    class Meta:
        model = TemplateImages
        fields = ('__all__')


class CreateContact(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('__all__')

class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscribe
        fields = ('email', )



class OrderTempateForm(forms.ModelForm):
    class Meta:
        model = TemplateOrder
        fields = ('email', 'country', 'first_name', 'last_name')



class FormCreatePage(forms.ModelForm):
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

class FormCreateTemplate(forms.ModelForm):
    class Meta:
        model = Template
        fields = ('title', 'price', 'demo', 'category', 'tags', 'body', 'tols','body', 'file' )


class PostSearchForm(forms.Form):
    q = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['q'].label = 'Search For'
        self.fields['q'].widget.attrs.update(
            {'class': 'form-control'})
       


