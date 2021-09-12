from django.db import models
from datetime import datetime

class Comment(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    comment = models.TextField()
    created = models.DateField(auto_now_add=True)

class Like(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    created = models.DateField(auto_now_add=True)


class Bookmark(models.Model):
    user_id = models.IntegerField()
    post_id = models.IntegerField()
    created = models.DateField(auto_now_add=True)

class Follow(models.Model):
    follower = models.IntegerField()
    followed = models.IntegerField()
    created = models.DateField(auto_now_add=True)
