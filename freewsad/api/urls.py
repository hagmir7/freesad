from .views import *
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('', home),
    path('create-post/', postCreate),
    path('create-topic', createPost),
    path('book/<int:id>', bookDetail),
    path('books/<int:num_books>/', BookListView.as_view()),
    path('posts/<int:num_posts>/', PostListView.as_view()),
    path('contact', contact_api,),
    path('post/<slug:slug>', postDetail),
    path('post/language/', postLanguage , name='post_language'),
    path('post/category/<int:id>', postCategoryFilter, name="post_category"),
    path('post/category/', postCategoryList),
    path('post/category/crud/<int:id>', postCategory ),
    path('post/delete/<int:id>', postDelete, name='post_delete_api'),
    path('post/create/', createPost),
    path('post/update/<int:id>', updatePost),
    path('post/id/<int:id>', getPostForUpdate),
    path('post/list/crud/<int:id>', postListCrud),
    path('post/play-list/', postList),
    path('all/posts/play-lists', allPostList ),
    path('play-list/posts/<int:id>', playListPosts), # list of posts that contain the current play list
    path('book/category/<int:id>', bookCategory, name="book_category"),
    path('book/list/crud/<int:id>', bookListCrud),
    path('book/list/', bookList),
    path('language/crud/<int:id>', languageCrud),
    path('language/list', language),
    path('search', search),

    # Dashboard
    path('dashboard/tools', dashboardTools),




    # Product paths
    path("save-email", saveEmails),

    path('all-post', getPoas),
    path('user/<slug:username>', user),
    path('user/id/<int:id>', userId),
    path('update/user/<slug:username>', updateUserInfo),
    path('delete/user/<slug:username>', deleteUser),
    # update profile
    path('update/profile/<int:id>', updateProfile),
    path('update/avatar/<int:id>', avatarUpdate),


    path('register', register),

    # JWT URLs
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('post/get/', getPosts),

    path('book/create', createBook),
    path('book/update/<int:id>', updateBook),
    path('books', books)




]
