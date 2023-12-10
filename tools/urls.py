from django.urls import path

from .views import *

urlpatterns = [
    path("links/", LinkCreateView.as_view(), name="links"),
    path("links/delete/", delete_link, name="delete_link"),
    path("links/update/<int:id>", update_link, name="update_link"),
    
    path("facebook/group/create/", create_facebook_group, name="create_facebook_group"),
    path('facebook/group/update/<int:pk>/', update_facebook_group, name='update_facebook_group'),
    path('facebook/group/delete/<int:pk>/', delete_facebook_group, name='delete_facebook_group'),


    path("facebook/account/create/", create_account, name="create_account"),
    path('facebook/account/update/<int:pk>/', update_account, name='update_account'),
    path('facebook/account/delete/<int:pk>/', delete_account, name='delete_account'),
]
