from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from freewsad.sitemaps import *
from django.contrib.sitemaps.views import sitemap
from rest_framework import routers

from freewsad.views import AdsView








router = routers.DefaultRouter()


sitemaps = {
    'static': StaticViewSitemap,
    'posts': PostsSitemap,
    # 'books': BookSitemap,
    # 'profile':ProfileSitemap,
    # 'templates':TemplateSitemap,
}


urlpatterns = [
    # path('i18n/', include('django.conf.urls.i18n')),
    path('summernote/', include('django_summernote.urls')),
    # SEO Tools
    path('robots.txt', include('robots.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('ads.txt', AdsView.as_view()),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('freewsad.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/', include('freewsad.api.urls')),
    path('api-all/', include(router.urls)),
    path('', include('users.urls')),
)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

