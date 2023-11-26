from django.urls import path

from . import views

urlpatterns = [
    path("links/", views.LinkCreateView.as_view(), name="links"),
    path("links/delete/", views.delete_link, name="delete_link"),
    path("links/update/<int:id>", views.update_link, name="update_link"),
]
