from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Post, Group, User
from django.conf import settings


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).all()[
        :settings.NUMBER_POSTS]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, template, context)


def profile(request, username):
    author = User.objects.get(username=username)
    posts = Post.objects.filter(author=author).all()
    quantity = len(posts)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # qantity = 'заглушка для колво'
    context = {
        'page_obj': page_obj,
        'username': username,
        'qantity': quantity,
    }
    return render(request, 'posts/profile.html', context)

def post_detail(request, post_id):
    author = User.objects.get(posts=post_id)
    post = get_object_or_404(Post, pk=post_id)
    quantity = Post.objects.filter(author=author).count()
    context = {
        'post': post,
        'quantity': quantity,
        'author': author,
    }
    return render(request, 'posts/post_detail.html', context)
