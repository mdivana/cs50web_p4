import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.views.generic import CreateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from .models import Post, User, Follow, Like


def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


# Added function-based view to see feed
def post_list(request, username=None):
    if username is not None:
        user = User.objects.get(username=username)
        following = Follow.objects.filter(follower=user).values('following')
        following_list = User.objects.filter(id__in=following)
        posts = Post.objects.filter(author__in=following_list).order_by('-date_posted')
    else:
        posts = Post.objects.order_by('-date_posted')

    for post in posts:
        post.likes = Like.objects.filter(post=post.id).count()
        post.save()

    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {
        'posts': posts,
    }

    return render(request, 'network/post_list.html', context)


# Added function-based view for profile
# Have to add following/follower count
def profile(request, username):
    posts = Post.objects.filter(author__username=username).order_by('-date_posted')
    follower_count = Follow.objects.filter(following__username=username).count()
    following_count = Follow.objects.filter(follower__username=username).count()
    is_following = None
    if request.user is not None:
        is_following = Follow.objects.filter(following__username=username, follower=request.user).exists()
    for post in posts:
        post.likes = Like.objects.filter(post=post.id).count()
        post.save()
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    context = {
        'posts': posts,
        'follower_count': follower_count,
        'following_count': following_count,
        'profile_username': username,
        'is_following': is_following,
    }
    return render(request, 'network/post_list.html', context)


@login_required
def follow(request, username):
    following_user = request.user
    following = User.objects.get(username=username)
    follow_object = Follow.objects.create(following=following, follower=following_user)
    # Additional logic or actions if needed
    return redirect('profile', username=username)

@login_required
def unfollow(request, username):
    following_user = request.user
    following = User.objects.get(username=username)
    Follow.objects.filter(following=following, follower=following_user).delete()
    # Additional logic or actions if needed
    return redirect('profile', username=username)


# Added function-based view for detailed version of post
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.likes = Like.objects.filter(post=post.id).count()
    post.save()
    post = get_object_or_404(Post, pk=post.id)
    likes = Like.objects.filter(post=post)
    liked_by_user = request.user.id in likes.values_list('user__id', flat=True)
    context = {
        'post': post,
        'liked_by_user': liked_by_user,
    }
    return render(request, 'network/post_detail.html', context)
    

# Added post creation by class-based view
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# Added post deletion by class-based view
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


# Added function for API route to handle edit user-side
@csrf_exempt
@login_required
def edit(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("content") is not None:
            post.content = data["content"]
        post.save()
        return HttpResponse(status=204)
    

# Added function for API route to handle like functionality user-side
@csrf_exempt
@login_required
def like(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.method == "GET":
        return JsonResponse(post.serialize())

    if request.method == "PUT":
        data = json.loads(request.body)
        if data.get("likes"):
            Like.objects.create(user=request.user, post=post)
            post.likes = Like.objects.filter(post=post).count()
        else:  # unlike
            Like.objects.filter(user=request.user, post=post).delete()
            post.likes = Like.objects.filter(post=post).count()
        post.save()
        return HttpResponse(status=204)