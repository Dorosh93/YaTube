from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm
from django.conf import settings


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count_post = posts.count()
    paginator = Paginator(posts, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists()
    context = {
        'author': author,
        'count_post': count_post,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    title = str(post)
    count_post = Post.objects.filter(author=post.author).count()
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'count_post': count_post,
        'title_post': title,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


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


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if post.author == request.user:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = form.save()
            return redirect('posts:post_detail', post_id)
        form = PostForm(instance=post)
        return render(request, 'posts/create_post.html',
                      {'form': form, 'is_edit': is_edit, 'post_id': post_id, })
    return redirect('posts:post_detail', post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, settings.POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    if request.user.username != username:
        Follow.objects.get_or_create(
            user=request.user,
            author=get_object_or_404(User, username=username),
        )
        return redirect('posts:profile', username)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    follow = Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username),
    )
    if follow.exists():
        follow.delete()
        return redirect('posts:profile', username)
    return redirect('posts:profile', username)
