from django.urls import path
from .views import post_detail, post_share, post_comment, post_list, post_search
from .feeds import LatestPostFeed

app_name = 'blog_app'


urlpatterns = [
#     path("", PostListView.as_view(), name="post_list"),
    path('', post_list, name = 'post_list'),
    path("<int:year>/<int:month>/<int:day>/<slug:post>", 
         post_detail, name="post_detail"),
    path('<int:post_id>/share/',
         post_share, name="post_share"),
    path('<int:post_id>/comment/', 
         post_comment, name ='post_comment'),
    path('tags/<slug:tag_slug>', post_list, name = 'post_list_by_tag'),
    path('feed/', LatestPostFeed(), name = 'post_feed'),
    path('search/', post_search, name = 'search')
]
