from django import template
from ..models import BlogPost
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.simple_tag
def total_posts():
    return BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).count()


@register.inclusion_tag('blog_app/post/latest_posts.html')
def show_latest_posts(count=3):
    latest_posts = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).order_by('-publish')[:count]
    return {'latest_posts':latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5):
    return BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]
    
@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))