from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Book, Language, Post
from users.models import Profile
import math
from django.conf import settings

class StaticViewSitemap(Sitemap):

    def items(self):
        return ['home']
    
    def location(self, items):
        return reverse(items)


class PostsSitemap(Sitemap):

    limit = 1000  # Number of items per page

    def items(self):
        langauge = Language.objects.get(id=1)
        return Post.objects.filter(language=langauge)

    def get_urls(self, page=1, site=None, protocol=None):
        # Override the get_urls method to return URLs for a specific page
        self.page = page
        return super().get_urls(page, site, protocol)
    
    def lastmod(self, obj):
        # Logic to determine the last modification date for each URL
        return obj.created

    def _get_pagination_urls(self):
        urls = []
        num_pages = int(math.ceil(self.paginator.count / float(self.limit)))
        for page in range(1, num_pages + 1):
            urls.extend(self.get_urls(page=page))
        return urls
    

    def get_url_info(self, obj):
        # Override the get_url_info method to include additional info for each URL
        info = super().get_url_info(obj)
        info['priority'] = 0.5  # Set the priority for the URL
        return info
    




# class BookSitemap(Sitemap):
#     def items(self):
#         return Book.objects.all()

    
# class ProfileSitemap(Sitemap):
#     def items(self):
#         return Profile.objects.all()
    
 