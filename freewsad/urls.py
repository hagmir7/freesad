from unicodedata import name
from django.urls import path
from .views import *
from .sites.dev import dev
from .sites.geeksforgeeks import geeksforgeeks
from .sites.cloud import cloud
from .sites.codingnepalweb import codingnepalweb
from .sites.book import books as book_scraping
from .sites.airlet import airlet
from .sites.kotobati import kotobati, scraping_kotobati
from .sites.zpdf import zpdf
from .sites.pdf import pdf
from .sites.dpdf import dpdf
from .sites.bdebooks import bdebooks
from .sites.pdfjatt import pdfjatt


urlpatterns = [
    path("", index, name="home"),
    # Post
    path("p/<slug:slug>", post, name="post"),
    path("post/create", createPost, name="create_post"),
    path("post/update/<int:id>", updatePost, name="update_post"),
    path("post/delete/<int:id>", deletePost, name="delete_post"),
    path("post/list", postList, name="posts_list"),
    path("post/create/category", createPostCategory, name="post.category.create"),
    path(
        "post/update/category/<int:id>", updatePostCategory, name="update_post_category"
    ),
    path(
        "post/delete/category/<int:id>", deletePostCategory, name="delete_post_category"
    ),
    path("post/category/list", postCategoryList, name="category_post_list"),
    path("post/status/<int:id>", postStatus, name="post-status"),
    path("category/<str:category>", category, name="category"),
    path("posts", posts, name="post.list"),
    # Pages
    path("page/create", createPage, name="create_page"),
    path("pages", pages, name="pages"),
    path("page/<slug:slug>", page, name="page"),
    path("page/delete/<int:id>", deletePage, name="delete_page"),
    path("page/update/<int:id>", updatePage, name="update_page"),
    path("book/rapport/<str:slug>", book_rapport, name="book_rapport"),
    path("rapport", rapport),
    # Search post
    path("search", search, name="search"),
    path("contact", contact, name="contact"),
    path("lable/<str:lable>", lable, name="lable"),
    path("menu", menu, name="menu"),
    path(
        "change_language/<str:language_code>", change_language, name="change_language"
    ),
    # Dashboard
    path("dashboard", dashboard, name="dashboard"),
    path("logs/", logs, name="logs"),
    # Books
    path("book/create", createBook, name="create_book"),
    path("book/list", bookList, name="books_list"),
    path("book/<str:slug>", bookDetail, name="book_detail"),
    path("books", books, name="books"),
    path("books/trending", trending_books, name="trending_books"),
    path("book/remove/<str:slug>", removeBook, name="remove_book"),
    path("books/new", new_books, name="new_books"),
    path("book/update/<int:id>", updateBook, name="update_book"),
    path("book/create/ai", createBookAi, name="create_ai_book"),
    path("book/create/category", createBookCategory, name="create_book_category"),
    path(
        "book/update/category/<int:id>", updateBookCategory, name="update_book_category"
    ),
    path(
        "book/delete/category/<int:id>", deleteBookCategory, name="delete_book_category"
    ),
    path("book/category/list", bookCategoryList, name="category_book_list"),
    path("book/delete/<int:id>", deleteBook, name="book_delete"),
    path("clear/history", clearHistory),
    path("clear/token", clearTokns),
    # path('lang', languagUpdate),
    # Scraping
    path("dev", dev),
    path("geeksforgeeks", geeksforgeeks),
    path("cloud", cloud),
    path("codingnepalweb", codingnepalweb),
    path("book-scraping", book_scraping),
    path("airlet", airlet),
    path("kotobati", kotobati),
    path("zpdf", zpdf),
    path("dpdf", dpdf),
    path("pdf", pdf),
    # emport Export
    path("posts/export", export_post),
    path("add-books-slug", addBooksSlug),
    path("book-file-exists", bookFileExists),
    path("update-post-body", updateBody),
    path(
        "video/comment/create/<str:slug>",
        create_video_comment,
        name="create_video_comment",
    ),
    # Video
    path("video/create", create_video, name="create_video"),
    path("videos", videos, name="videos"),
    path("upload/<str:slug>", quality_upload, name="upload_video"),
    path("video/<str:slug>", video, name="video"),
    path("video/list/create", create_video_list, name="create_video_list"),
    path("quality/delete/<int:id>", delete_quality, name="delete_quality"),
    path("video/comments/<str:slug>", video_comments, name="video_comments"),
    path(
        "video/comment/delete/<int:id>",
        delete_video_comment,
        name="delete_video_comment",
    ),
    # Scraping
    path("scraping/kotobati", scraping_kotobati),
    # path("extra/space", remove_extra_space_book_title_author),
    # Delete duplicated
    path("delete/duplicated/books", duplicated_books, name="duplicated_books"),
    # path("clean", clean_book),
    path("upload", upload_file, name="upload_file"),
    path("bdebooks", bdebooks),
    path("pdfjatt", pdfjatt),
    # path("upload_page", upload_page),
]
