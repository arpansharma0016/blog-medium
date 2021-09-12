from django.contrib import admin
from .models import Post, Connect, Me, Confirm, Password, Draft

admin.site.register(Post)
admin.site.register(Confirm)
admin.site.register(Connect)
admin.site.register(Me)
admin.site.register(Password)
admin.site.register(Draft)

# Register your models here.
