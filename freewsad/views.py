from .models import BookView
from django.db.models.functions import TruncDate
from django.http import Http404, HttpResponseRedirect,JsonResponse, HttpResponse, HttpResponseBadRequest
from django_user_agents.utils import get_user_agent
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from . forms import *
from django.views import View
from .export import PostResource
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from bs4 import BeautifulSoup
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _
from django.utils import translation, timezone
from datetime import timedelta
from django.core.files.storage import FileSystemStorage
from .config.save import  *
import mimetypes


def superuser_required(user):
    if not user.is_superuser:
        raise PermissionDenied
    return True


def change_language(request, language_code):
    if language_code in [lang[0] for lang in settings.LANGUAGES]:
        translation.activate(language_code)
        request.session["django_language"] = language_code
    return redirect(request.META.get('HTTP_REFERER'))


class AdsView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'ads.txt')


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
@staff_member_required
def logs(request):
    log_file_path = os.path.join('logse/passenger.log')  # Replace with the actual path to the log file
    with open(log_file_path, 'r') as log_file:
        log_contents = log_file.read()
    return render(request, 'logs.html', {'log_contents': log_contents})


def index(request):
    query = request.GET.get('query')


    # if query is not None:
    #     title = Post.objects.filter(title__icontains=query)
    #     description = Post.objects.filter(description__icontains=query)
    #     posts = title | description
    # else:
    #     posts = Post.objects.filter(language__code=request.LANGUAGE_CODE, is_public=True).order_by('-created')[0:16]

    if query is not None:
        name = Book().filler().filter(name__icontains=query)
        description = Book().filler().filter(description__icontains=query)
        tags = Book().filler().filter(tags__icontains=query)
        books = name | description | tags
    else:
        books = Book().filler().filter(language__code=request.LANGUAGE_CODE).order_by('-created_at')[0:24]

    # if query is not None:
    #     title = Video.objects.filter(title__icontains=query)
    #     description = Video.objects.filter(description__icontains=query)
    #     tags = Video.objects.filter(tags__icontains=query)
    #     videos = title | description | tags
    # else:
    #     videos = Video.objects.filter(language__code=request.LANGUAGE_CODE).order_by('-created_at')[0:16]


    context = {
        # 'posts': posts,
        # 'videos': videos,
        'query' : query if query else '',
        'books' : books,
        'title':  _('Freesad - Articles') if 'posts' in request.path else None
    }
    return render(request, 'index.html', context)

def posts(request):
    query = request.GET.get("query")

    if query is not None:
        title = Post.objects.filter(title__icontains=query)
        description = Post.objects.filter(description__icontains=query)
        posts = title | description
    else:
        posts = Post.objects.filter(
            language__code=request.LANGUAGE_CODE, is_public=True
        ).order_by("-created")[0:16]

        context = {
            'posts': posts,
            # 'videos': videos,
            "query": query if query else "",
            # "books": books,
            "title": _("Freesad - Articles") if "posts" in request.path else None,
        }
    return render(request, "post/list.html", context)


# @user_passes_test(is_admin)
# @staff_member_required
def postStatus(request, id):
    post = get_object_or_404(Post, id=id)
    if post.is_public:
        post.is_public = False
        post.save()
    else:
        post.is_public = True
        post.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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
        'tags' : post.tags

    }
    return render(request, 'post/post.html', context)


def bodyParser(body, title):
    soup = BeautifulSoup(body, 'html.parser')

    images = soup.find_all('img')
    for image in images:
        image['alt'] = title
        image['height'] = 'auto'
        image['width'] = '100%'
        if 'freesad' not in image['src']:
            image['src'] = 'https://www.freesad.com' + image['src']  # Combine base URL with relative image source
    return str(soup)


@user_passes_test(is_admin)
def createPost(request):
    form = CreatePostForm()
    playList = PostList.objects.filter(user=request.user)
    category = PostCategory.objects.all()
    language = Language.objects.all()
    if request.method == "POST":
        form = CreatePostForm(request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.body = bodyParser(obj.body, obj.title)
            obj.user = request.user
            obj.save()
            messages.success(request, _("Post Creaeted successfully.."))
            return redirect('create_post')
    context = {
        'form': form,
        'lists': playList,
        'category': category,
        'language': language,
        'title': 'Create Post'
    }
    return render(request, 'post/create.html', context)


@user_passes_test(is_admin)
def updatePost(request, id):
    post = get_object_or_404(Post, id=id)
    form = CreatePostForm(instance=post)
    playList = PostList.objects.filter(user=request.user)
    category = PostCategory.objects.all()
    language =Language.objects.all()
    if request.method == "POST":
        form = CreatePostForm(request.POST, files=request.FILES, instance=post)
        if form.is_valid():
            if post.user == request.user or request.user.is_superuser:
                obj = form.save(commit=False)
                obj.body = bodyParser(obj.body, obj.title)
                obj.save()
                messages.success(request, _('The post updated successfully.'))
                return redirect('home')
            else:
                messages.warning(request, _('You cannot update the post'))
                return redirect('home')

    context = {
        "form": form,
        'title': 'Update Post',
        'lists': playList,
        'category': category,
        'language' : language
    }
    return render(request, 'post/update.html', context)

@user_passes_test(is_admin)
def deletePost(request, id):
    post = get_object_or_404(Post, id=id)
    if post.user == request.user:
        post.delete()
        messages.success(request, _("Post deleted successfull."))
        return redirect('posts_list')
    else:
        return redirect('posts_list')


@user_passes_test(is_admin)
def postList(request):
    if request.user.is_superuser:
        query = request.GET.get('query')
        if query:
            title = Post.objects.filter(title__icontains=query).order_by('created')
            id = Post.objects.filter(id__icontains=query).order_by('created')
            description = Post.objects.filter(description__icontains=query).order_by('created')
            list = title | id | description
        else:
            list = Post.objects.all().order_by('-created')
        paginator = Paginator(list, 50) 
        page_number = request.GET.get('page')
        posts = paginator.get_page(page_number)
        count = Post.objects.all().count()
        context = {'posts': posts, 'count': count, 'query': query if query else '' }
        return render(request, 'post/auth-list.html', context)
    else:
        return redirect('home')


@user_passes_test(is_admin)
def postCategoryList(request):
    if request.user.is_superuser:
        list = PostCategory.objects.all().order_by('-id')
        paginator = Paginator(list, 50) 
        page_number = request.GET.get('page')
        category = paginator.get_page(page_number)
        count = PostCategory.objects.all().count()
        context = {'category': category, 'count': count }
        return render(request, 'post/category/auth-list.html', context)
    else:
        return redirect('home')

# Category list
def category(request, category):
    current_category = get_object_or_404(PostCategory, slug=category)
    list = Post.objects.filter(category__slug=category).order_by('-created')
    paginator = Paginator(list, 24)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    context = {
        'posts': posts,
        'title' : current_category.name,
    }
    return render(request, 'index.html', context)


@user_passes_test(is_admin)
def createPostCategory(request):
    form = FromPostCategory()
    if request.method == 'POST':
        form = FromPostCategory(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Category created successfully...'))
            return redirect('post.category.create')
    context = {
        'form': form,
        'title': 'Create category'
    }
    return render(request, 'post/category/create.html', context)


@user_passes_test(is_admin)
def updatePostCategory(request, id):
    if request.user.is_superuser:
        category = get_object_or_404(PostCategory, id=id)
        form = FromPostCategory(instance=category)
        if request.method == 'POST':
            form = FromPostCategory(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, _('Category updated successfully...'))
                return redirect('category_post_list')
        context = {
            'form': form,
            'title': 'Update category'
        }
        return render(request, 'post/category/update.html', context)


@user_passes_test(is_admin)
def deletePostCategory(request, id):
    category = get_object_or_404(PostCategory, id=id)
    if request.user.is_superuser:
        if category.delete():
            messages.success(request, _('Category deleted successfully...'))
            return redirect('category_post_list')
        else:
            messages.success(request, _('Fail to delete category.'))
            return redirect('category_post_list')
    else:
        return redirect('home')


# ------------------------ Book Views ----------------------


# def books(request):
#     list = Book().filler().annotate(views_count=Count('views')).filter(language__code=request.LANGUAGE_CODE).order_by('-views_count')
#     paginator = Paginator(list, 30)
#     page_number = request.GET.get('page')
#     books = paginator.get_page(page_number)
#     count = Book.books.all().count()
#     context = {'books': books, 'count': count, 'title': _("Most popular books - Freesad")}
#     return render(request, 'book/list.html', context)


def books(request):
    books_query = Book.objects.filter(language__code=request.LANGUAGE_CODE)
    books_count = books_query.count()

    books_list = books_query.annotate(views_count=Count("views")).order_by(
        "-views_count"
    )

    paginator = Paginator(books_list, 30)
    page_number = request.GET.get("page")
    books = paginator.get_page(page_number)

    context = {
        "books": books,
        "count": books_count,
        "title": _("Most popular books - Freesad"),
    }
    return render(request, "book/list.html", context)


def new_books(request):
    list = Book.books.filter(language__code=request.LANGUAGE_CODE).order_by('-created_at')
    paginator = Paginator(list, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    count = Book.books.all().count()
    context = {
        "books": books,
        "count": count,
        "title": _("Most popular books - Freesad"),
    }
    return render(request, 'book/list.html', context)


def trending_books(request):
    list = Book.books.filter(language__code=request.LANGUAGE_CODE).order_by('?')
    paginator = Paginator(list, 30)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    count = Book.books.all().count()
    context = {'books': books, 'count': count, 'title': _("Most popular books - Freesad")}
    return render(request, 'book/list.html', context)


# def trending_books(request):
#     seven_days_ago = timezone.now() - timedelta(days=7)

#     books = Book.books.filter(
#         language__code=request.LANGUAGE_CODE,
#         bookview__created_at__gte=seven_days_ago
#     ).annotate(views_count=Count('bookview')).order_by('-views_count')

#     paginator = Paginator(books, 30)
#     page_number = request.GET.get('page')
#     books_page = paginator.get_page(page_number)

#     context = {
#         'books': books_page,
#         'title': _("Most popular books - Freesad")
#     }
#     return render(request, 'book/list.html', context)

def bookDetail(request, slug):
    book = get_object_or_404(Book , slug=slug)
    if book.removed:
        raise Http404("The requested resource was not found.")
    books = Book().filler().filter(category=book.category).order_by('?')[0:12]

    agent = get_user_agent(request)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if not Location.objects.filter(ip=ip).exists():
        location = Location.objects.create(
            ip=ip,
            os=agent.os[0],
            browser=agent.browser[0],
        )
    else:
        location = Location.objects.get(ip=ip)
    if not location in book.views.all():
        book.views.add(location)
        try:
            book.save()
        except:
            pass

    videos = Video.objects.all()[0:14]

    context = {
        'title' : book.name if book.name else book.title,
        'description' : book.description,
        'image': book.image,
        'book': book,
        'tags': book.tags,
        'videos': videos,
        'books': books
    }

    return render(request, 'book/book.html', context)


# -------------------------  Book list
@user_passes_test(is_admin)
def bookList(request):
    query = request.GET.get('query')
    if query:
        name = Book.objects.filter(name__icontains=query)
        id = Book.objects.filter(id__icontains=query)
        description = Book.objects.filter(description__icontains=query)
        list = name | id | description
    else:
        list = Book.objects.all()
    paginator = Paginator(list, 50) 
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    count = Book.objects.all().count()
    context = {'books': books, 'count': count, 'query': query if query else ''}
    return render(request, 'book/auth-list.html', context)


@user_passes_test(is_admin)
def createBook(request):
    form = BookForm()
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        allowed_extensions = ['.txt', '.pdf', '.epub']
        file_extension = os.path.splitext(file.name)[1]
        if file_extension.lower() not in allowed_extensions:
            return HttpResponseBadRequest("Invalid file type. Only .txt, .pdf and epub files are allowed.")
        else:
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
    }
    return render(request, 'book/create.html', context)


from .sites.robo import bot


def getBookTitle(name: str, lang: str, book_type: str):
    if lang == 'ar':
        title = f"تحميل {book_type} {name} PDF مجانا"
    elif lang == 'en':
        title = f"Download {name} free PDF {book_type}"
    else:
        title = f"Télécharger {name} gratuitement en PDF {book_type}"
    return title


@user_passes_test(is_admin)
def createBookAi(request):
    form = BookAiForm()
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        allowed_extensions = ['.txt', '.pdf', '.epub']
        file_extension = os.path.splitext(file.name)[1]
        if file_extension.lower() not in allowed_extensions:
            return HttpResponseBadRequest("Invalid file type. Only .txt, .pdf and epub files are allowed.")
        else:
            form = BookAiForm(request.POST, files=request.FILES)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.user = request.user

                obj.language = obj.category.language
                obj.title = getBookTitle(obj.name, obj.category.language.code, obj.type.name)
                obj.tags = bot(f"return to me meta keyword for ({obj.title}) in on line by comma")
                obj.description = bot(f"return to me a long description for ({obj.title}) evry paragraph in <p> tag")
                obj.save()
                messages.success(request, 'Book created successfully.')
                return redirect('create_book')
            else:
                messages.warning(request, 'Fail to create a Book.')
                return redirect('create_book')

    context = {
        'form': form,
        'title': 'Create Book',
    }
    return render(request, 'book/create.html', context)


@user_passes_test(is_admin)
def updateBook(request, id):
    book = get_object_or_404(Book, id=id)
    if request.user.is_superuser or request.user == book.user:
        form = BookForm(instance=book)
        if request.method == "POST":
            form = BookForm(request.POST, instance=book, files=request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, _('Book updated successfully...'))
                return redirect('update_book', id=book.id)
        context = {
            'form': form,
            'book' : book,
            'title': 'Create Book',
        }
    else:
        return redirect('home')
    return render(request, 'book/update.html', context)


@user_passes_test(is_admin)
def deleteBook(request, id):
    book = get_object_or_404(Book, id=id)
    try:
        book.delete()
        messages.success(request, _("Book deleted successfully."))
    except Exception as e:
        messages.error(request, _("An error occurred: ") + str(e))
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


@user_passes_test(is_admin)
def createBookCategory(request):
    if request.user.is_superuser:
        form = FormBookCategory()
        if request.method == 'POST':
            form = FormBookCategory(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _('Category created successfully...'))
                return redirect('category_book_list')
            else:
                print("not valid")
        context = {
            'form': form,
            'title': 'Create category'
        }
        return render(request, 'book/category/create.html', context)


@user_passes_test(is_admin)
def updateBookCategory(request, id):
    if request.user.is_superuser:
        category = get_object_or_404(BookCategory, id=id)
        form = FormBookCategory(instance=category)
        if request.method == 'POST':
            form = FormBookCategory(request.POST, instance=category)
            if form.is_valid():
                form.save()
                messages.success(request, _('Category updated successfully...'))
                return redirect('category_book_list')
        context = {
            'form': form,
            'title': 'Update category'
        }
        return render(request, 'book/category/create.html', context)


@user_passes_test(is_admin)
def deleteBookCategory(request, id):
    category = get_object_or_404(BookCategory, id=id)
    if request.user.is_superuser:
        if category.delete():
            messages.success(request, _('Category deleted successfully...'))
            return redirect('category_book_list')
        else:
            messages.success(request, _('Category deleted successfully...'))
            return redirect('category_book_list')
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
    page = get_object_or_404(Page, id=id)
    form = FormCreatePage(instance=page)
    if request.method == 'POST' and request.user.is_superuser:
        form = FormCreatePage(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect('pages')
    context = {"form": form}
    return render(request, 'page/update.html', context)


@user_passes_test(is_admin)
def deletePage(request, id):
    page = get_object_or_404(Page, id=id)
    operation = page.delete()
    if operation:
        messages.success(request, _('Page deleted successfully.'))
        return redirect('pages')

    else:
        messages.warning(request, _('Fail to delete page.'))
        return redirect('pages')


def lable(request, lable):
    posts = Post.objects.filter(tags__icontains=lable, is_public=True, language__code=request.LANGUAGE_CODE)
    context = {"posts": posts, 'title': f"{lable} - Freesad"}
    return render(request, 'lable.html', context)

def menu(request):
    context = {'title': _('Menu - Freesad')}
    return render(request, 'menu.html', context)


def contact(request):
    form = CreateContact()
    if request.method == "POST":
        form = CreateContact(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('The message has been sent successfully'))
            return redirect('contact')
    context = {'form':form,'title': _('Freesad - Contace')}
    return render(request, 'contact/contact.html', context)


@user_passes_test(is_admin)
def contactList(request):
    list = Contact.objects.all().order_by('-date')
    paginator = Paginator(list, 20)
    page_number = request.GET.get('page')
    contacts = paginator.get_page(page_number)
    context = {
        "contacts": contacts,
        "title": _("Contaces list - Freesad"),
        "contact_count": Contact.objects.filter(readed=False),
    }
    return render(request, 'contact/list.html', context)

@user_passes_test(is_admin)
def contactSavedList(request):
    list = Contact.objects.filter(saved=True).order_by('-date')
    paginator = Paginator(list, 20)
    page_number = request.GET.get('page')
    contacts = paginator.get_page(page_number)
    context = {
        "contacts": contacts,
        "title": _("Saved Contaces list - Freesad"),
        "contact_count": list.count(),
    }
    return render(request, 'contact/list.html', context)


@user_passes_test(is_admin)
def contactShow(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.readed = True
    contact.save()
    context = {'contact':contact,'title': contact.name}
    return render(request, 'contact/show.html', context)

@user_passes_test(is_admin)
def contactSave(request, id):
    contact = get_object_or_404(Contact, id=id)
    if contact.saved:
        contact.saved = False
        messages.success(request, message=_("Message unsaved successfully!"))
    else:
        contact.saved = True
        messages.success(request, message=_("Message unsaved successfully!"))
    contact.save()
    return redirect('/contact/list')

@user_passes_test(is_admin)
def contactDelete(request, id):
    contact = get_object_or_404(Contact, id=id)
    contact.delete()
    messages.success(request, message=_("Message deleted successfully!"))
    return redirect('/contact/list')


@user_passes_test(is_admin)
def dashboard(request):
    users = User.objects.all().count()
    posts = Post.objects.all().count()
    books = Book.books.all().count()
    views = Location.objects.all().count()
    context = {
        "users" : users,
        "posts" : posts,
        "views" : views,
        'books' : books
    }
    return render(request, 'dashboard/index.html', context)


from django.contrib.admin.models import LogEntry;

def clearHistory(request):
    LogEntry.objects.all().delete()
    return redirect('/')

from rest_framework_simplejwt.tokens import BlacklistedToken, OutstandingToken


def clearTokns(request):
    return True
    OutstandingToken.objects.all().delete()
    return redirect('/')


def languagUpdate(request):
    return True
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


def addBooksSlug(request):
    books = Book.books.all()
    for book in books:
        book.views = book.views + 1
        book.save()
    return redirect('/')


def bookFileExists(request):
    books = Book.books.all()
    for book in books:
        file_path = os.path.join(settings.MEDIA_ROOT, str(book.file))
        if os.path.exists(file_path):
            pass
        else:
            print(f"File does not exist for book: {book.id}")
    return redirect('/')


# --------------------- Post Play List  ----------------------

@user_passes_test(is_admin)
def postPlayList(request):
    query = request.GET.get('query')
    if query:
        list = Post.objects.filter(title__icontains=query)
    else:
        list = Post.objects.all()
    paginator = Paginator(list, 20)
    page_number = request.GET.get('page')
    playList = paginator.get_page(page_number)

    context = {
        'title' : 'Post play lists',
        'lists' : playList
    }
    return render(request, 'list/auth-list.html', context)


@user_passes_test(is_admin)
def deletePostPlayList(request, id):
    list = get_object_or_404(PostList, id=id)
    list.delete()
    messages.success(request, _("Play list deleted successfully."))
    return redirect('/post/play-lists/list')


def updateBody(request):
    return False
    posts = Post.objects.all()
    for post in posts:
        post.body = bodyParser(post.body, post.title)
        post.save()
    return redirect('/')


# Video
@user_passes_test(superuser_required)
def create_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
            return redirect(f'/upload/{video.slug}')
    else:
        form = VideoForm()
    return render(request, 'video/create.html', {'form': form})


@user_passes_test(is_admin)
def update_video(request, slug):
    video = Video.objects.get(slug=slug)
    form = VideoForm(request.POST, request.FILES, instance=video)
    if form.is_valid():
        form.save()
        messages.success(request, _("Video updated successfully."))
        return redirect(f'/video/{video.slug}')
    return render(request, 'video/create.html', {'form': form, 'video': video})

@user_passes_test(superuser_required)
def delete_video(request, id):
    video = get_object_or_404(Video, id=id)
    video.delete()
    messages.success(request, _("Video deleted successfully."))
    return redirect('/')


def videos(request):
    videos_list = Video.objects.filter(language__code=request.LANGUAGE_CODE).order_by('-created_at')
    paginator = Paginator(videos_list, 16)
    page_number = request.GET.get('page')
    videos = paginator.get_page(page_number)

    context = {'videos': videos}
    return render(request, 'video/list.html', context)


def video(request, slug):
    video = get_object_or_404(Video, slug=slug)
    qualities = Quality.objects.filter(video=video)

    # List Vides (Order By views)
    list_videos = Video.objects.annotate(views_count=Count('views')).filter(language__code=request.LANGUAGE_CODE).order_by('-views_count')[0:14]
    paginator = Paginator(list_videos, 24)
    page_number = request.GET.get("page")
    videos = paginator.get_page(page_number)


    agent = get_user_agent(request)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if not Location.objects.filter(ip=ip).exists():
        location = Location.objects.create(
            ip=ip,
            os=agent.os[0],
            browser=agent.browser[0],
        )
    else:
        location = Location.objects.get(ip=ip)
    if not location in video.views.all():
        video.views.add(location)
        video.save()


    context = {
        'video': video,
        'videos': videos,
        'title': video.title,
        'qualities': qualities,
        'image': video.image
    }

    return render(request, 'video/show.html', context)


# Quality
@user_passes_test(superuser_required)
def quality_upload(request, slug):
    video = get_object_or_404(Video, slug=slug)
    qualities = Quality.objects.filter(video=video)
    if request.method == 'POST':
        form = QualityForm(request.POST, request.FILES)
        if form.is_valid():
            quality = form.save(commit=False)
            quality.video = video
            quality.save()
            return JsonResponse({'message': _("Video uploaded successfully.")})
        else:
            return JsonResponse({'message': _("Fail to upload Video")}, status=500)

    else:
        form = QualityForm()
    context = {
        'form': form,
        'video': video,
        'qualities': qualities
    }
    return render(request, 'video/quality/upload.html', context)

@user_passes_test(is_admin)
def update_quality(request, slug):
    quality = Quality.objects.get(slug=slug)
    form = QualityForm(request.POST, request.FILES, instance=quality)
    if form.is_valid():
        form.save()
        messages.success(request, _("quality updated successfully."))
        return redirect(f'/video/update/{quality.video.slug}')
    return render(request, 'video/quality/update.html', {'form': form, 'quality': quality})


@user_passes_test(superuser_required)
def delete_quality(request, id):
    video = get_object_or_404(Quality, id=id)
    video.delete()
    messages.success(request, _("Quality delete successfully"))
    return redirect(request.META.get('HTTP_REFERER'))


from freewsad.api.serializers import VideoCommentSerializer

# Video Comment
def create_video_comment(request, slug):
    video = get_object_or_404(Video, slug=slug)
    if request.method == 'POST':
        form = VideoCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.video = video
            comment.save()
            serializer = VideoCommentSerializer(comment)
            return JsonResponse(serializer.data, safe=False)
        else:
            return JsonResponse({"message": _("Fail to create comment")}, status=403)
    return JsonResponse({"message": _("Method not allowd.")}, status=403)


def video_comments(request, slug):
    video = get_object_or_404(Video, slug=slug)
    comments_list = VideoComment.objects.filter(video=video).order_by("-created_at")
    paginator = Paginator(comments_list, 10)
    page_number = request.GET.get("page")
    comments = paginator.get_page(page_number)
    serializer = VideoCommentSerializer(comments, many=True)
    return JsonResponse({"data": serializer.data, "has_next": comments.has_next()}, safe=False)

@user_passes_test(is_admin)
def delete_video_comment(request, id):
    video = get_object_or_404(VideoComment, id=id)
    if video.user == request.user or request.user.is_superuser:
        video.delete()
        return JsonResponse({"message": _('Comment deleted successfully!')})
    else:
        raise Http404("Page not found")

@user_passes_test(is_admin)
def create_video_list(request):
    form = VideoListForm()
    if request.method == 'POST':
        form = VideoListForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.save()
            return redirect('create_video')
    context = {
        'form' : form
    }
    return render(request, 'video/list/create.html', context)


def book_rapport(request, slug):
    try:
        book = Book.books.get(slug=slug)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=404)

    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)  # Last seven days including today

    dates = [seven_days_ago + timedelta(days=i) for i in range(7)]

    book_views = BookView.objects.filter(
        book=book,
        created_at__date__range=(seven_days_ago, today)
    ).annotate(date=TruncDate('created_at')).values('date').annotate(views_count=Count('id')).order_by('date')

    date_to_views = {entry['date']: entry['views_count'] for entry in book_views}

    report_data = [
        {
            'date': date.strftime('%Y-%m-%d'),
            'views_count': date_to_views.get(date, 0),
        }
        for date in dates
    ]

    book_report = {
        'book_name': book.name,  # Replace with the actual attribute representing the book's name
        'book_report': report_data,
    }

    return JsonResponse(book_report)


@user_passes_test(is_admin)
def removeBook(request, slug):
    book = get_object_or_404(Book, slug=slug)
    book.remove()
    messages.success(request, _("Book Removed successfully!"))
    return redirect("/book/list")

def rapport(request):
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=6)  # Last seven days including today
    
    dates = [seven_days_ago + timedelta(days=i) for i in range(7)]
    
    book_counts = Book.books.filter(created_at__date__range=(seven_days_ago, today)).values('created_at__date').annotate(book_count=models.Count('id'))

    user_counts = User.objects.filter(date_joined__date__range=(seven_days_ago, today)).values('date_joined__date').annotate(user_count=models.Count('id'))

    # location_counts = Location.objects.filter(created_at__date__range=(seven_days_ago, today)).values('created_at__date').annotate(location_count=models.Count('id'))




    book_data_count = {entry['created_at__date']: entry['book_count'] for entry in book_counts}

    user_data_count = {entry['date_joined__date']: entry['user_count'] for entry in user_counts}

    # location_data_count = {entry['created_at__date']: entry['location_count'] for entry in location_counts}
    
    book = [
        {
            'date': date.strftime('%Y-%m-%d'),
            'count': book_data_count.get(date, 0),
        }
        for date in dates
    ]


    user = [
        {
            'date': date.strftime('%Y-%m-%d'),
            'count': user_data_count.get(date, 0),
        }
        for date in dates
    ]

    # views = [
    #     {
    #         'date': date.strftime('%Y-%m-%d'),
    #         'count': location_data_count.get(date, 0),
    #     }
    #     for date in dates
    # ]
    
    rapport = {
        'books': book,
        'users': user,
        # 'views': views
    }
    
    return JsonResponse(rapport)


def remove_extra_spaces(string):
    return False
    return " ".join(string.split())

def remove_extra_space_book_title_author(request):
    return False
    books = Book.objects.all()
    for book in books:
        books.title = remove_extra_spaces(book.title)
        book.author = remove_extra_spaces(book.author)
        book.save()
    return JsonResponse({"message": "success"})


# Remove duplicated

def duplicated_books(request):
    # duplicated_data = Book.objects.values('name').annotate(name_count=Count('name')).filter(name_count__gt=1)
    # for item in duplicated_data:
    #         name = item['name']
    #         duplicates = Book.objects.filter(name=name)
    #         if duplicates.count() > 1:
    #             duplicates = duplicates[:duplicates.count()-1] # Exclude the first occurrence
            
    #         for duplicate in duplicates:
    #             duplicate.delete()
    return redirect("home")


def clean_book(request):
    books = Book.objects.filter(name__icontains="DOWNLOAD")
    for book in books:
        book.name = book.name.replace("( DOWNLOAD) ", "")
        book.name = book.name.replace(" PDF", "")
        book.name = book.name.replace(" )", ")")
        book.title = book.title.replace("( DOWNLOAD) ", "")
        book.title = book.title.replace(" )", ")")
        try:
            book.save()
        except:
            print(book.title)
    return redirect("home")


def upload_file(request):
    file_url = None

    if request.method == "POST" and request.FILES.get("file"):
        
        book_name = request.POST.get("name")
        if Book.objects.filter(name=book_name):
            messages.warning(request, message="File is alredy exitst", extra_tags='info')
            return redirect("/upload")
        
        uploaded_file = request.FILES["file"]

        
        file_name = uploaded_file.name
        file_extension = os.path.splitext(file_name)[1].lower()

        if file_extension == ".pdf":
            # Further check the MIME type
            mime_type, _ = mimetypes.guess_type(file_name)

            if mime_type == "application/pdf":
                # Save the file
                fs = FileSystemStorage()
                new_file_name = f"{random_slug(10).upper()}-freesad.com.pdf"
                if settings.CPANEL:
                    filename = fs.save(f"/home/agha6919/freesad.com/media/PDF/{new_file_name}", uploaded_file)
                else:
                    filename = fs.save(f"PDF/{new_file_name}", uploaded_file)

                file_url = fs.url(filename)
                file_path = fs.path(filename)
                file_data = get_pdf_info(file_path, book_name)

                # Add file path to file data
                file_data["file"] = file_url
                file_data["size"] = get_file_size(file_path)

                # Save file
                Book.objects.create(
                    name=book_name,
                    author=file_data["author"],
                    description=file_data["description"],
                    tags=file_data["keywords"],
                    image=str(file_data["image"]).replace("/home/agha6919/freesad.com/media/", ""),
                    book_type=file_data["extantion"],
                    pages=file_data["pages"],
                    file=file_data["file"].replace("media/", ""),
                    size=file_data["size"],
                    status=True,
                    slug=file_data["slug"],
                    title=file_data["title"],
                    language=Language.objects.get(id=1),
                    user=User.objects.get(id=1),
                    category=BookCategory.objects.get(id=1),
                )
                messages.success(request, message="File created successfully.", extra_tags="success")
                return redirect("/upload")
            
            else:
                messages.error(request, message="The uploaded file is not a valid PDF.", extra_tags="danger")
                return redirect("/upload")
    return render(request, "upload.html", {"file_url": file_url})


from openai import OpenAI


OPENAI_API_KEY = settings.AI_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


content = """
You are an SEO assistant with extensive knowledge about books. 
When I provide you with the name of a author, please return a detailed description in HTML and put eche paragraph in p tag.
"""
def get_author(book_name):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "",
            },
            {
                "role": "user",
                "content": book_name,
            },
        ],
    )

    return list(list(completion.choices[0].message)[0])[1]


def ai(request):
    if request.GET.get("author"):
        return JsonResponse({"message": get_author(request.GET.get("author"))})
    return HttpResponse("No author name")


# views.py
def remove_books(request):
    if request.method == 'POST':
        slugs = request.POST.get('slugs', '').strip()

        if not slugs:
            messages.error(request, 'Slugs field is required.')
            return redirect('remove_books')
        
        slugs_list = list(filter(None, map(str.strip, slugs.splitlines())))

        if slugs_list:
            # Change this line to delete books instead of updating
            deleted_books_count = Book.objects.filter(slug__in=slugs_list).delete()[0]
            messages.success(request, f'{deleted_books_count} books were removed.')
            return redirect("remove_books")
        else:
            messages.error(request, 'No valid slugs found.')
    
    return render(request, "remove_books.html")
