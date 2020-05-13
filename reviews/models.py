from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager
# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=30)
    director = models.CharField(max_length=30)
    actors = models.TextField()
    description = models.TextField()
    poster_url = models.TextField()
    open_date = models.DateTimeField()
    audience_num = models.IntegerField(default=0)
    def __str__(self):
        return self.title

class Review(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    rank = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    view_count = models.IntegerField(default=0)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_reivews')
    tags = TaggableManager()


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')