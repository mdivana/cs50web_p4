from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    pass

class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=70)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0, blank=True, null=True, editable=False)

    def serialize(self):
        return {
            "id": self.id,
            "likes": self.likes
        }
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="likeduser")
    post = models.ForeignKey(Post, on_delete=models.PROTECT, related_name="likedpost")


class Follow(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")  # user's followings
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")  # user's followers