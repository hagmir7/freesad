from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Book, Language, Post, Template
from users.models import Profile

class StaticViewSitemap(Sitemap):

    def items(self):
        return ['home']
    
    def location(self, items):
        return reverse(items)


class PostsSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    def items(self):
        langauge = Language.objects.get(id=1)
        return Post.objects.filter(language=langauge)


# class BookSitemap(Sitemap):
#     def items(self):
#         return Book.objects.all()

    
# class ProfileSitemap(Sitemap):
#     def items(self):
#         return Profile.objects.all()
    
    
# class TemplateSitemap(Sitemap):
#     def items(self):
#         return Template.objects.all()