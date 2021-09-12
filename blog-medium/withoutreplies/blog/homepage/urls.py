from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="index"),
    # path('comment-<str:username>-<int:post_id>-<str:comment>/', views.comment, name="comment"),
    # path('edit_comment-<str:username>-<int:post_id>-<str:comment>/', views.edit_comment, name="edit_comment"),
    # path('delete_comment-<str:username>-<int:post_id>/', views.delete_comment, name="delete_comment"),
    # path('get_comment-<str:username>-<int:post_id>/', views.get_comment, name="get_comment"),
    path('like-<str:username>-<int:post_id>/', views.like, name="like"),
    path('bookmark-<str:username>-<int:post_id>/', views.bookmark, name="bookmark"),
    path('follow-<str:username>-<int:post_id>/', views.follow, name="follow"),
    path('follow_user-<str:username>/', views.follow_user, name="follow_user"),
    path('search/', views.search, name="search"),
    path('<str:username>/', views.author, name="author"),
    path('<str:username>/followers/', views.followers, name="followers"),
    path('<str:username>/following/', views.following, name="author"),
    path('<str:username>/<str:title>-<int:post_id>/', views.post, name="post"),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)