from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from me.models import Post, Draft, Me, Connect
from django.contrib.auth.models import User, auth
from .models import Comment, Like, Bookmark, Follow
from django.contrib import messages
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import random
import math
from django.contrib.auth.hashers import make_password
import os
from slugify import slugify

def index(request):
    return render(request, "index.html")

def post(request, username, title, post_id):
    con = Connect.objects.filter(username=username).first()
    if not con:
        request.session['next'] = "write"
        messages.info(request, "You need to Login First!")
        return redirect("login")

    usr = Me.objects.filter(user_id=con.id).first()
    if not usr:
        request.session['next'] = "write"
        messages.info(request, "You need to Login First!")
        return redirect("login")
    
    posts = Post.objects.filter(user_id=con.id)
    po = posts.filter(id=post_id).first()
    if not slugify(po.title) == title:
        return redirect("post", username=username, title=slugify(po.title), post_id=po.id)
    tags = po.tags
    tags = tags[1:len(tags)-1]
    tag = tags.split(',')
    
    comments = Comment.objects.filter(post_id=post_id)
    likes = Like.objects.filter(post_id=po.id)

    if request.user.is_authenticated:
        curr_con = Connect.objects.filter(username=request.user.username).first()
        if not curr_con:
            request.session['next'] = f"post({username}, {po.title}, {post_id})"
            messages.info(request, "You need to Login First!")
            return redirect("login")

        curr_usr = Me.objects.filter(user_id=curr_con.id).first()
        if not curr_usr:
            request.session['next'] = f"post({username}, {po.title}, {post_id})"
            messages.info(request, "You need to Login First!")
            return redirect("login")

        co = comments.filter(user_id=curr_con.id).first()
        like = likes.filter(user_id=curr_con.id)
        bookmark = Bookmark.objects.filter(post_id=po.id).filter(user_id=curr_con.id).first()
        follow = Follow.objects.filter(follower=curr_con.id).filter(followed=con.id).first()
        
    else:
        curr_con = None
        curr_usr = None
        co = None
        like = None
        bookmark = None
        follow = None


    di = dict()
    for c in comments:
        conn = Connect.objects.filter(id=c.user_id).first()
        usrr = Me.objects.filter(user_id=conn.id).first()
        di[conn] = usrr

    posts = posts[0:4]

    context = {
        'con':con,
        'usr':usr,
        'po':po,
        'tags':tag,
        'posts':posts,
        'curr_con':curr_con,
        'curr_usr':curr_usr,
        'comments':comments,
        'di':di,
        'co':co,
        'likes':likes,
        'like':like,
        'bookmark':bookmark,
        'follow':follow
    }

    return render(request, "post.html", context)

def search(request):
    return render(request, "search.html")

def author(request, username):
    con = get_object_or_404(Connect, username=username)
    if not con:
        return redirect("/")

    usr = get_object_or_404(Me, user_id=con.id)
    if not usr:
        return redirect("/")

    posts = Post.objects.filter(user_id=con.id)

    if request.user.is_authenticated:
        curr_con = Connect.objects.filter(username=request.user.username).first()
        curr_usr = Me.objects.filter(user_id=curr_con.id).first()
        follow = Follow.objects.filter(follower=curr_con.id).filter(followed=con.id).first()
    
    else:
        curr_con = None
        curr_usr = None
        follow = None


    context = {
        'con':con,
        'usr':usr,
        'posts':posts,
        'curr_con':curr_con,
        'curr_usr':curr_usr,
        'follow':follow
    }
    return render(request, "author.html", context)

def comment(request, username, post_id, comment):
    if request.user.is_authenticated:
        po = Post.objects.filter(id=post_id).first()
        con = Connect.objects.filter(username=request.user.username).first()
        if not con:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        usr = Me.objects.filter(user_id=con.id).first()
        if not usr:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        co = Comment.objects.filter(user_id=con.id).filter(post_id=post_id)
        cof = co.first()
        if not co.exists():
            cof = Comment.objects.create(user_id=con.id, post_id=post_id, comment=comment)
            cof.save()

        comment = cof.comment
        return JsonResponse({'status':'success', 'comment':comment})
    else:
        return JsonResponse({'status':'login', 'next':f'?next=/{username}/{po.title}-{post_id}'})


def delete_comment(request, username, post_id):
    if request.user.is_authenticated:
        con = Connect.objects.filter(username=request.user.username).first()
        po = Post.objects.filter(id=post_id).first()
        if not po:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        if not con:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        co = Comment.objects.filter(user_id=con.id).filter(post_id=post_id)
        cof = co.first()
        if co.exists():
            cof.delete()
        return JsonResponse({'status':'success'})

    else:
        return JsonResponse({'status':'login', 'next':f'?next=/{username}/{po.title}-{post_id}'})

def get_comment(request, username, post_id):
    if request.user.is_authenticated:
        con = Connect.objects.filter(username=request.user.username).first()
        po = Post.objects.filter(id=post_id).first()
        if not po:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        if not con:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        co = Comment.objects.filter(user_id=con.id).filter(post_id=post_id)
        cof = co.first()
        if co.exists():
            return JsonResponse({'status':'success', 'comment':cof.comment})
        else:
            return JsonResponse({'status':'success', 'comment':''})

    else:
        return JsonResponse({'status':'login', 'next':f'?next=/{username}/{po.title}-{post_id}'})


def edit_comment(request, username, post_id, comment):
    if request.user.is_authenticated:
        con = Connect.objects.filter(username=request.user.username).first()
        po = Post.objects.filter(id=post_id).first()
        if not po:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        if not con:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        co = Comment.objects.filter(user_id=con.id).filter(post_id=post_id)
        cof = co.first()
        if co.exists():
            cof.comment = comment
            cof.save()
            return JsonResponse({'status':'success', 'comment':cof.comment})
        else:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

    else:
        return JsonResponse({'status':'login', 'next':f'?next=/{username}/{po.title}-{post_id}'})


def like(request, username, post_id):
    if request.user.is_authenticated:
        con = Connect.objects.filter(username=request.user.username).first()
        po = Post.objects.filter(id=post_id).first()
        if not po:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        if not con:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        if Like.objects.filter(user_id=con.id).filter(post_id=po.id).exists():
            like = Like.objects.filter(user_id=con.id).filter(post_id=po.id).first()
            like.delete()
            return JsonResponse({'status':'success', 'like':'deleted'})
        else:
            like = Like.objects.create(user_id=con.id, post_id=po.id)
            like.save()
            return JsonResponse({'status':'success', 'like':'created'})

    else:
        return JsonResponse({'status':'login', 'next':f'?next=/{username}/{po.title}-{post_id}'})


def bookmark(request, username, post_id):
    if request.user.is_authenticated:
        con = Connect.objects.filter(username=request.user.username).first()
        po = Post.objects.filter(id=post_id).first()
        if not po:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        if not con:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        if Bookmark.objects.filter(user_id=con.id).filter(post_id=po.id).exists():
            bookmark = Bookmark.objects.filter(user_id=con.id).filter(post_id=po.id).first()
            bookmark.delete()
            return JsonResponse({'status':'success', 'bookmark':'deleted'})
        else:
            bookmark = Bookmark.objects.create(user_id=con.id, post_id=po.id)
            bookmark.save()
            return JsonResponse({'status':'success', 'bookmark':'created'})

    else:
        return JsonResponse({'status':'login', 'next':f'?next=/{username}/{po.title}-{post_id}'})


def follow(request, username, post_id):
    if request.user.is_authenticated:
        con = Connect.objects.filter(username=username).first()
        curr_con = Connect.objects.filter(username=request.user.username).first()
        po = Post.objects.filter(id=post_id).first()
        if not po:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        if not curr_con:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        if not con:
            return JsonResponse({'status':'fail', 'next':f'/{username}/{po.title}-{post_id}'})

        fol = Follow.objects.filter(follower=curr_con.id).filter(followed=con.id)
        if fol.exists():
            follow = fol.first()
            follow.delete()
            return JsonResponse({'status':'success', 'follow':'deleted'})
        else:
            follow = Follow.objects.create(follower=curr_con.id, followed=con.id)
            follow.save()
            return JsonResponse({'status':'success', 'follow':'created'})

    else:
        return JsonResponse({'status':'login', 'next':f'?next=/{username}/{po.title}-{post_id}'})



def follow_user(request, username,):
    if request.user.is_authenticated:
        con = Connect.objects.filter(username=username).first()
        curr_con = Connect.objects.filter(username=request.user.username).first()

        if not curr_con:
            return JsonResponse({'status':'fail', 'next':f'/{username}/'})

        if not con:
            return JsonResponse({'status':'fail', 'next':f'/{username}/'})

        fol = Follow.objects.filter(follower=curr_con.id).filter(followed=con.id)
        if fol.exists():
            follow = fol.first()
            follow.delete()
            return JsonResponse({'status':'success', 'follow':'deleted'})
        else:
            follow = Follow.objects.create(follower=curr_con.id, followed=con.id)
            follow.save()
            return JsonResponse({'status':'success', 'follow':'created'})

    else:
        return JsonResponse({'status':'login', 'next':f'?next=/{username}/'})