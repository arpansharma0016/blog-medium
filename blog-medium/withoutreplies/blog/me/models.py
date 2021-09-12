from django.db import models
from datetime import datetime

class Connect(models.Model):
    username = models.TextField()

import os
def image_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.user_id}.{ext}"
    folder = os.path.join('uploads/', str(instance.user_id))
    return os.path.join(folder, filename)

class Me(models.Model):
    user_id = models.IntegerField()
    image = models.ImageField(null=True, blank=True, upload_to=image_name)
    name = models.TextField()
    bio = models.TextField()

class Confirm(models.Model):
    username = models.TextField()
    name = models.TextField()
    email = models.TextField()
    password = models.TextField()
    otp = models.TextField()
    attempts = models.IntegerField(default=0)

class Password(models.Model):
    username = models.TextField()
    otp = models.TextField()
    confirmed = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)

class Post(models.Model):
    user_id = models.IntegerField()
    thumbnail = models.TextField()
    title=models.TextField()
    caption=models.TextField()
    post=models.TextField()
    post_json=models.TextField()
    tags = models.TextField()
    created = models.DateField(auto_now_add=True)


class Draft(models.Model):
    user_id = models.IntegerField()
    thumbnail = models.TextField()
    title=models.TextField()
    caption=models.TextField()
    post=models.TextField()
    post_json=models.TextField()
    tags = models.TextField()
    created = models.DateField(auto_now_add=True)

