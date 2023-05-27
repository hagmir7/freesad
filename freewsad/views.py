from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from agmir.settings import LANGUAGE_CODE
from . forms import *
from django.http import HttpResponse
from django.views import View
import random
from users.models import Profile
from .export import PostResource


class AdsView(View):
    def get(self, request, *args, **kwargs):
        line  =  "google.com, pub-6043226569102012, DIRECT, f08c47fec0942fa00"
        return HttpResponse(line)


def index(request):

    query = request.GET.get('query')
    if query is not None:
        title = Post.objects.filter(title__icontains=query)
        description = Post.objects.filter(description__icontains=query)
        list = title | description
    else:
        list = Post.objects.filter(language=1, is_public=True).order_by('-created')

    paginator = Paginator(list, 14) 
    page_number = request.GET.get('page')
    post = paginator.get_page(page_number)
    context = {
        'posts': post,
        'query' : query if query else ''
    }
    return render(request, 'index.html', context)


# Post search

def search(request):
    if request.method == 'POST':
        query = request.POST['search']
        post_title = Post.objects.filter(title__icontains=query)
        post_desc = Post.objects.filter(description__icontains=query)
        post_body = Post.objects.filter(body__icontains=query)
        posts = post_desc | post_title | post_body
        context = {'posts':posts, 'title':query}
    else:
        return redirect('home')
        context = {}
    
    return render(request, 'index.html',context)


def post(request, slug):
    post = get_object_or_404(Post, slug=slug)
    list = Post.objects.filter(language=post.language, category=post.category).order_by('-created')[:3]


    context = {
        'post':post,
        'description': post.description,
        'title': post.title,
        'posts': list,
        'image': post.image,

    }
    return render(request, 'post/post.html', context)

@login_required
def createPost(request):
    form = CreatePostForm()
    playList = PostList.objects.filter(user=request.user)
    category = PostCategory.objects.all()
    language = Language.objects.all()
    if request.method == "POST":
        form = CreatePostForm(request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            messages.success(request, "Post Creaeted successfully..")
            return redirect('create_post')
    context = {
        'form': form,
        'lists': playList,
        'category': category,
        'language': language,
        'title': 'Create Post'
    }
    return render(request, 'post/create.html', context)



@login_required
def updatePost(request, id):
    post = Post.objects.get(id=id)
    form = CreatePostForm(instance=post)
    playList = PostList.objects.filter(user=request.user)
    category = PostCategory.objects.all()
    language =Language.objects.all()
    if request.method == "POST":
        form = CreatePostForm(request.POST, files=request.FILES, instance=post)
        if form.is_valid():
            if post.user == request.user or request.user.is_superuser:
                form.save()
                messages.success(request, 'The post updated successfully.')
                return redirect('home')
            else:
                messages.warning(request, 'You cannot update the post')
                return redirect('home')

    context = {
        "form": form,
        'title': 'Update Post',
        'lists': playList,
        'category': category,
        'language' : language
    }
    return render(request, 'post/update.html', context)

@login_required
def deletePost(request, id):
    post = get_object_or_404(Post, id=id)
    if post.user == request.user:
        post.delete()
        messages.success(request, "Post deleted successfull.")
        return redirect('posts_list')
    else:
        return redirect('posts_list')

@login_required
def postList(request):
    if request.user.is_superuser:
        list = Post.objects.all().order_by('-created')
        paginator = Paginator(list, 50) 
        page_number = request.GET.get('page')
        posts = paginator.get_page(page_number)
        count = Post.objects.all().count()
        context = {'posts': posts, 'count': count}
        return render(request, 'post/auth-list.html', context)
    else:
        return redirect('home')
@login_required
def postCategoryList(request):
    if request.user.is_superuser:
        list = PostCategory.objects.all().order_by('-id')
        paginator = Paginator(list, 50) 
        page_number = request.GET.get('page')
        category = paginator.get_page(page_number)
        count = PostCategory.objects.all().count()
        context = {'category': category, 'count': count}
        return render(request, 'post/category/auth-list.html', context)
    else:
        return redirect('home')
    
# Category list
def category(request, category):
    list = Post.objects.filter(category__name=category).order_by('-created')
    paginator = Paginator(list, 24)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'title' : "All Categories"
        }
    return render(request, 'index.html', context)

@login_required    
def createPostCategory(request):
    if request.user.is_superuser:
        form = FromPostCategory()
        if request.method == 'POST':
            form = FromPostCategory(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category created successfully...')
                return redirect('category_post_list')
        context = {
            'form': form,
            'title': 'Create category'
        }
        return render(request, 'post/category/create.html', context)

@login_required
def updatePostCategory(request, id):
   if request.user.is_superuser:
        category = PostCategory.objects.get(id=id)
        form = FromPostCategory(instance=category)
        if request.method == 'POST':
            form = FromPostCategory(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category updated successfully...')
                return redirect('category_post_list')
        context = {
            'form': form,
            'title': 'Update category'
        }
        return render(request, 'post/category/update.html', context)

@login_required
def deletePostCategory(request, id):
    category = PostCategory.objects.get(id=id)
    if request.user.is_superuser:
        if category.delete():
            messages.success(request, 'Category deleted successfully...')
            return redirect('category_post_list')
        else:
            messages.success(request, 'Category deleted successfully...')
            return redirect('category_post_list')
    else:
        return redirect('home')


def convet(request):
    posts = Post.objects.filter(category=3)
    posts2 = Post.objects.filter(category=2)
    post1 = Post.objects.filter(category=1)
    for post in posts:
        post.language = 3
        post.save()
    for post in posts2:
        post.language = 2
        post.save()
    for post in post1:
        post.language = 1
        post.save()
    return redirect('home')

# ------------------------ Book Views ----------------------


def books(request):
    list = Book.objects.filter(language__code=request.LANGUAGE_CODE).order_by('-date')
    paginator = Paginator(list, 30) 
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    count = Book.objects.all().count()
    context = {'books': books, 'count': count, 'title': "Books - Freesad"}
    return render(request, 'book/list.html', context)

@login_required
def bookDetail(request, id=id):
    book = get_object_or_404(Book , id=id)
    book.addView()
    context = {
        'title' : book.name,
        'description' : book.description,
        'image': book.image,
        'book': book
    }
    return render(request, 'book/book.html', context)

@login_required
def bookList(request):
    if request.user.is_superuser:
        list = Book.objects.all().order_by('-date')
        paginator = Paginator(list, 50) 
        page_number = request.GET.get('page')
        books = paginator.get_page(page_number)
        count = Book.objects.all().count()
        context = {'books': books, 'count': count}
        return render(request, 'book/auth-list.html', context)
    else:
        return redirect('home')


@login_required
def createBook(request):
    if request.user.is_superuser:
        category = BookCategory.objects.all()
        form = BookForm()
        language = Language.objects.all()
        if request.method == "POST":
            form = BookForm(request.POST, files=request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.user = request.user
                obj.save()
                messages.success(request, 'Book created successfully.')
                return redirect('create_book')
            else:
                messages.warning(request, 'Fail to create a Book.')
                return redirect('create_book')
        context = {
            'form': form,
            'title': 'Create Book',
            'category': category,
            'language': language,
            'file_type': type_book
        }
    else:
        return redirect('home')
    return render(request, 'book/create.html', context)


@login_required
def updateBook(request, id):
    book = Book.objects.get(id=id)
    if request.user.is_superuser and request.user == book.user:
        category = BookCategory.objects.all()
        form = BookForm(instance=book)
        language = Language.objects.all()
        if request.method == "POST":
            form = BookForm(request.POST, instance=book, files=request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Book updated successfully...')
                return redirect('books_list')
        context = {
            'form': form,
            'title': 'Create Book',
            'category': category,
            'file_type': type_book,
            'language': language
        }
    else:
        return redirect('home')
    return render(request, 'book/update.html', context)


@login_required
def deleteBook(request, id):
    book = get_object_or_404(Book, id=id)
    if book.user == request.user:
        book.delete()
        messages.success(request, "Book deleted successfull.")
        return redirect('books_list')
    else:
        return redirect('books_list')


def bookCategoryList(request):
    if request.user.is_superuser:
        list = BookCategory.objects.all().order_by('-id')
        paginator = Paginator(list, 50) 
        page_number = request.GET.get('page')
        category = paginator.get_page(page_number)
        count = BookCategory.objects.all().count()
        context = {'category': category, 'count': count}
        return render(request, 'book/category/auth-list.html', context)
    else:
        return redirect('home')

def createBookCategory(request):
    if request.user.is_superuser:
        form = FormBookCategory()
        if request.method == 'POST':
            form = FormBookCategory(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category created successfully...')
                return redirect('category_book_list')
        context = {
            'form': form,
            'title': 'Create category'
        }
        return render(request, 'book/category/create.html', context)


def updateBookCategory(request, id):
   if request.user.is_superuser:
        category = BookCategory.objects.get(id=id)
        form = FormBookCategory(instance=category)
        if request.method == 'POST':
            form = FormBookCategory(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, 'Category updated successfully...')
                return redirect('category_book_list')
        context = {
            'form': form,
            'title': 'Update category'
        }
        return render(request, 'book/category/update.html', context)


def deleteBookCategory(request, id):
    category = BookCategory.objects.get(id=id)
    if request.user.is_superuser:
        if category.delete():
            messages.success(request, 'Category deleted successfully...')
            return redirect('category_book_list')
        else:
            messages.success(request, 'Category deleted successfully...')
            return redirect('category_book_list')
    else:
        return redirect('home')


# ------------------------ Template Views ----------------------

def templeteList(request):
    if request.user.is_superuser:
        list = Template.objects.all().order_by('-date')
        paginator = Paginator(list, 50) 
        page_number = request.GET.get('page')
        templates = paginator.get_page(page_number)
        count = Template.objects.all().count()
        context = {'templates': templates, 'count': count}
        return render(request, 'template/auth-list.html', context)
    else:
        return redirect('home')






def deleteTemplate(request, id):
    template = get_object_or_404(Template, id=id)
    if template.user == request.user:
        template.delete()
        messages.success(request, "Template deleted successfull.")
        return redirect('templates_list')
    else:
        return redirect('templates_list')


def templates(request):
    list = Template.objects.all().order_by('-date')
    paginator = Paginator(list, 10) 
    page_number = request.GET.get('page')
    templates = paginator.get_page(page_number)
    count = Template.objects.all().count()
    context = {'templates': templates, 'count': count}
    context = {
        'templates': templates,
        'title': 'Templates'
    }
    return render(request, 'template/list.html', context)


def template(request, slug):
    template = Template.objects.get(slug=slug)
    context = {
        'template': template,
        'title': template.title,
        'description': template.body[0:150],
    }
    return render(request, 'template/template.html', context)

def createTemplate(request):
    if request.user.is_superuser:
        form = FormCreateTemplate()
        if request.method == 'POST':
            form = FormCreateTemplate(request.POST)
            images = []
            if form.is_valid():
                files = request.FILES.getlist('images')
                for file in files:
                    create_template = TemplateImages.objects.create(images=file)
                    images.append(create_template) 
                obj = form.save(commit=False)
                obj.user = request.user
                obj.save()
                for item in images:
                    obj.image.add(item)
                messages.success(request, 'Tempate created successfully...')
                return redirect('templates_list')
        context = {
            'form': form,
            'title': 'Create Template',
            'category': TemplatesCategory.objects.all(),
            'tols': TemplateTols.objects.all()
        }
        return render(request, 'template/create.html', context)
    else:
        return redirect('home')


# ------------------------ Page Views ----------------------

def page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    return render(request, 'page/page.html', {'page': page, "title": page.title})


def pages(request):
    pages = Page.objects.all().order_by('created')
    return render(request, 'page/list.html', {'pages': pages, "title": "Pages"})

def createPage(request):
    form = FormCreatePage()
    if request.method == 'POST' and request.user.is_superuser:
        form = FormCreatePage(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pages')
    context = {"form": form}
    return render(request, 'page/create.html', context)


def updatePage(request, id):
    page = Page.objects.get(id=id)
    form = FormCreatePage(instance=page)
    if request.method == 'POST' and request.user.is_superuser:
        form = FormCreatePage(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect('pages')
    context = {"form": form}
    return render(request, 'page/update.html', context)

def deletePage(request, id):
    page = Page.objects.get(id=id)
    if request.user.is_superuser:
        operation = page.delete()
        if operation:
            messages.success(request, 'Page deleted successfully.')
            return redirect('pages')

        else:
            messages.warning(request, 'Page deleted failde ')
            return redirect('pages')

    return redirect('home')


def lable(request, lable):
    posts = Post.objects.filter(tags__icontains=lable, is_public=True, language__code=request.LANGUAGE_CODE)
    context = {"posts": posts, 'title': f"{lable} - Freesad"}
    return render(request, 'lable.html', context)

def menu(request):
    context = {'title': 'Menu - Freesad'}
    return render(request, 'menu.html', context)






def contact(request):
    form = CreateContact()
    if request.method == "POST":
        form = CreateContact(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'The message has been sent successfully')
            return redirect('contact')
    context = {'form':form,'title':'Freesad - Contace'}
    return render(request, 'contact/contact.html', context)



def contactList(request):
    list = Contact.objects.all().order_by('created')
    paginator = Paginator(list, 20)
    page_number = request.GET.get('page')
    contacts = paginator.get_page(page_number)
    context = {'contacts':contacts,'title':'Freesad - Contaces list'}
    return render(request, 'contact/list.html', context)


@login_required
def dashboard(request):
    return render(request, 'dashboard/index.html')


from django.contrib.admin.models import LogEntry;

def clearHistory(request):
    LogEntry.objects.all().delete()
    return redirect('/')

from rest_framework_simplejwt.tokens import BlacklistedToken, OutstandingToken


def clearTokns(request):
    OutstandingToken.objects.all().delete()
    return redirect('/')



def languagUpdate(request):
    # Language.objects.create(id=1, name='English', code='en')
    # Language.objects.create(id=2, name='Français', code='fr')
    # Language.objects.create(id=3, name='العربية', code='ar')

    PostCategory.objects.create(id=1, name='Programming')
    PostCategory.objects.create(id=2, name='Programmation')
    PostCategory.objects.create(id=3, name='برمجة')
    return redirect('/')



# Export view
def export_post(request):
    post = PostResource()
    list = Post.objects.all()
    paginator = Paginator(list, 100) 
    page_number = request.GET.get('page')
    queryset = paginator.get_page(page_number)
    dataset = post.export(queryset)
    # Choose the desired export format (e.g., xlsx, csv)
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="exported_data.xlsx"'

    return response










