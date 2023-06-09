from django.urls import path

from . import views
from .views import PostCreateView, PostDeleteView


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('posts', views.post_list, name='post-list'),
    path('followings/posts/<str:username>', views.post_list, name='post-list-following'),
    path('user/<str:username>/', views.profile, name='profile'),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('unfollow/<str:username>/', views.unfollow, name='unfollow'),

    # API Routes
    path("edit/<int:post_id>/", views.edit, name="edit"),
    path("like/<int:post_id>", views.like, name="like"),
]
