
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from blog_app.sitemaps import PostSitemap

sitemaps = {
    'posts':PostSitemap,
}


urlpatterns = [
    path("admin/", admin.site.urls),
    path("blog/", include("blog_app.urls", namespace="blog_app")),
     path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
          name='django.contrib.sitemaps.views.sitemap'),
]
# /home/user/Desktop/Trenches/django_project/ml-apprentice/blog_app/urls.py