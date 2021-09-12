from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.me, name="me"),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('confirm_email/<str:uname>/', views.confirm_email, name='confirm_email'),
    path('resend_code/<str:uname>/', views.resend_code, name='resend_code'),
    path('enter_otp/<str:uname>/', views.enter_otp, name='enter_otp'),
    path('enter_otp/', views.forgot_password, name='forgot_password'),
    path('new_password/<str:uname>/', views.new_password, name='new_password'),
    path('resend_pass_code/<str:uname>/', views.resend_pass_code, name='resend_pass_code'),
    path('logout/', views.logout, name='logout'),
    path('delete_post-<int:post_id>/', views.delete_post, name="delete_post"),
    path('write/', views.write, name="write"),
    path('followers/', views.followers, name="followers"),
    path('remove_follower-<int:user_id>/', views.remove_follower, name="remove_follower"),
    path('following/', views.following, name="following"),
    path('delete_image/', views.delete_image, name="delete_image"),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)