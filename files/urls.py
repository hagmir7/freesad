from django.urls import path
from .views import *




urlpatterns = [
    path('files', files),
    path('file/delete/<int:id>', deleteFiles),

]
