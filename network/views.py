from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Post, User


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


# Added class-based views to see feed
# Might have to make function-based since class-based views won't update data without refresh
def post_list(request):
    posts = Post.objects.order_by('-date_posted')
    context = {
        'posts': posts,
    }
    return render(request, 'network/post_list.html', context)


@login_required
def user_post_list(request):
    posts = Post.objects.filter(author=request.user).order_by('-date_posted')
    context = {
        'posts': posts,
    }
    return render(request, 'network/post_list.html', context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'like':
            if request.user not in post.likes.all():
                post.likes.add(request.user)
        elif action == 'unlike':
            if request.user in post.likes.all():
                post.likes.remove(request.user)

        return redirect('post-detail', pk=pk)

    context = {
        'post': post,
    }
    return render(request, 'network/post_detail.html', context)


def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user not in post.likes.all():
        post.likes.add(request.user)

    return redirect('post-detail', pk=pk)


def unlike_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user in post.likes.all():
        post.likes.remove(request.user)

    return redirect('post-detail', pk=pk)
    

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
