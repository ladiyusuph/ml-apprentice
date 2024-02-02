from django.shortcuts import render, get_object_or_404
from .models import BlogPost, Comment
from django.http import Http404
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from .forms import EmailPostForm, CommentForm, SearchForm

# Create your views here.

# class PostListView(ListView):
#     """
#     Alternative post list view

#     Args:
#         ListView (ListView): _description_
#     """
#     queryset = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).all()
#     context_object_name = "posts"
#     paginate_by = 3
#     template_name = 'blog_app/post/post_list.html'

def post_list(request, tag_slug=None):
    post_list = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__name__in=[tag.name])
    paginator = Paginator(post_list, 3)
    page = request.GET.get('page', 1)
    try:
        posts = paginator.get_page(page)
    except PageNotAnInteger:
        posts = paginator.get_page(1)
    except EmptyPage:
        posts = paginator.get_page(paginator.num_pages)
    return render(request, 
                  'blog_app/post/post_list.html', 
                  {'posts':posts, 'tag':tag})



def post_detail(request, year, month, day, post):
    post = get_object_or_404(BlogPost, 
                             status=BlogPost.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    
    comments = post.comments.filter(active=True)
    
    form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).filter(tags__in=post_tags_ids)\
                                            .exclude(id=post.id)    
    similar_posts = similar_posts.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags', '-publish')[:4]
                                
    return render(request, 
                  'blog_app/post/post_detail.html', 
                  {'post':post,
                   'comments':comments,
                   'form':form,
                   'similar_posts':similar_posts})
    

def post_share(request, post_id):
    post = get_object_or_404(BlogPost,
                             id=post_id, 
                             status=BlogPost.Status.PUBLISHED)
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n {cd['name']}\'s comments: {cd['comments']}"
            
            send_mail(subject, message, 'yusuphmustaphaladi@gmail.com',
                      [cd['to']])
            sent = True            
    else:
        form = EmailPostForm()
        
    return render(request, 'blog_app/post/share.html', {'post':post,
                                                              'form':form,
                                                              'sent':sent})
    
    
    
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(BlogPost,
                             id=post_id,
                             status=BlogPost.Status.PUBLISHED)
    comment = None
    
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        
        comment.post = post
        comment.save()
        
    return render(request, 'blog_app/post/comment.html',
                  {'post':post,
                   'form':form,
                   'comment': comment})
    
def post_search(request):
    form = SearchForm()
    query = None
    results = []
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_vector = SearchVector('title', weight='A') +\
            #                 SearchVector('body', weight='B')
            # search_query = SearchQuery(query)
            # results = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).annotate(
            #     search=search_vector,
            #     rank=SearchRank(search_vector, search_query)
            # ).filter(rank__gte=0.3).order_by('-rank')
            results = BlogPost.objects.filter(status=BlogPost.Status.PUBLISHED).annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')
    return render(request,
                  'blog_app/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})