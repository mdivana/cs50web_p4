from django.urls import path

from . import views
from .views import PostCreateView, PostUpdateView, PostDeleteView


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('posts', views.post_list, name='post-list'),
    path('user/str:username>/', views.user_post_list, name='post-list-user'),
    path('post/<int:pk>/', views.post_detail, name='post-detail'),
    path('post/<int:pk>/like/', views.like_post, name='like-post'),
    path('post/<int:pk>/unlike/', views.unlike_post, name='unlike-post'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
]
