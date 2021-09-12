from django.contrib import admin

from .models import Like, Bookmark, Follow

# admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Bookmark)
admin.site.register(Follow)