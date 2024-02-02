import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import BlogPost

class LatestPostFeed(Feed):
    title = 'ML Apprentice'
    link = reverse_lazy('blog_app:post_list')
    description = "Latest Blog Posts"
    
    def items(self):
        return BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).all()[:5]
    
    def item_ttile(self, item):
        return item.title
    
    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.body), 30)
    
    def item_pubdate(self, item):
        return item.publish