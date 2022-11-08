from django.shortcuts import render, \
    get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from .utils import make_paginator


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.all()
    page_obj = make_paginator(posts, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()

    page_obj = make_paginator(posts, request)
    context = {
        'page_obj': page_obj,
        'group': group,
    }
    return render(request, template, context)


def profile(request, username):
    author = User.objects.get(username=username)
    posts = author.posts.all()
    page_obj = make_paginator(posts, request)
    context = {
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    author = User.objects.get(posts=post_id)
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'author': author,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST)
    template = 'posts/create_post.html'
    context = {
        'form': form,
    }
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author.username)
        return render(request, template, context)
    else:
        return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id != post.author.id:
        return redirect('posts:index')
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post.author = request.user
        post.save()
        return redirect('posts:post_detail', post_id=post.id)

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id

    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
