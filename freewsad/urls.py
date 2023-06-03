from unicodedata import name
from django.urls import path
from .views import *
from . sites.dev import dev
from . sites.geeksforgeeks import geeksforgeeks
from . sites.cloud import cloud
from . sites.codingnepalweb import codingnepalweb

urlpatterns = [
    path('', index, name='home'),
    # Post
    path('p/<slug:slug>',post ,name="post"),
    path('post/create', createPost, name="create_post"),
    path('post/update/<int:id>', updatePost, name='update_post'),
    path('post/delete/<int:id>', deletePost, name='delete_post'),
    path('post/list', postList ,name='posts_list'),
    path('post/create/category', createPostCategory, name='post.category.create'),
    path('post/update/category/<int:id>', updatePostCategory, name='update_post_category'),
    path('post/delete/category/<int:id>', deletePostCategory, name='delete_post_category'),
    path('post/category/list', postCategoryList,  name="category_post_list"),
    path('category/<str:category>', category, name='category'),
    path('posts', index, name="post.list"),
    # Pages
    path('page/create', createPage, name='create_page'),
    path('pages', pages, name='pages'),
    path('page/<slug:slug>', page, name='page'),
    path('page/delete/<int:id>', deletePage, name='delete_page'),
    path('page/update/<int:id>', updatePage, name='update_page'),

    # Search post
    path('search', search, name='search'),
    path('contact', contact, name='contact'),
    path('lable/<str:lable>', lable, name='lable'),
    path('menu', menu, name='menu'),




    # Dashboard
    path('dashboard', dashboard, name='dashboard'),  

    # Books
    path('book/create', createBook, name='create_book'),
    path('book/list', bookList, name='books_list'),
    path('book/<str:slug>', bookDetail, name="book_detail"),
    path('books', books, name='books'),
    path('book/delete/<int:id>', deleteBook, name='book_delete'),
    path('book/update/<int:id>', updateBook , name='update_book'),

    path('book/create/category', createBookCategory, name='create_book_category'),
    path('book/update/category/<int:id>', updateBookCategory, name='update_book_category'),
    path('book/delete/category/<int:id>', deleteBookCategory, name='delete_book_category'),
    path('book/category/list', bookCategoryList,  name="category_book_list"),


    path('convet', convet),
    path('clear/history', clearHistory),
    path('clear/token', clearTokns),
    # path('lang', languagUpdate),


    # Scraping
    path('dev',dev),
    path('geeksforgeeks', geeksforgeeks),
    path('cloud', cloud),
    path('codingnepalweb', codingnepalweb),


    # emport Export 
    path('posts/export', export_post),


    path('add-books-slug', addBooksSlug),
    path('book-file-exists', bookFileExists),




]


