from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Post, Group, Follow, User
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm


CNT_SORT = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, CNT_SORT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    pg_list = group.posts.all()
    paginator = Paginator(pg_list, CNT_SORT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user_post = author.posts.all()
    paginator = Paginator(user_post, CNT_SORT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    count_post = author.posts.count()
    context = {
        'author': author,
        'user_post': user_post,
        'page_obj': page_obj,
        'count_post': count_post
    }
    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user,
        author=author).exists()
    user = request.user
    if user.is_authenticated:
        foll_context = {
            'author': author,
            'user': user,
            'page_obj': page_obj,
            'following': following
        }
        return render(request, 'posts/profile.html', foll_context)
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    count_post = author.posts.count()
    group = post.group
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'count_post': count_post,
        'group': group,
        'comments': comments,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    post_create = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', post.author)
        return render(request, post_create, {'form': form})
    return render(request, post_create, {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.pk)
    context = {'form': form,
               'is_edit': True
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


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user).select_related('author', 'group')
    paginator = Paginator(posts, CNT_SORT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('posts:profile', username=username)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    follow = Follow.objects.filter(user=request.user, author=author)
    follow.delete()
    return redirect('posts:profile', username=author)
