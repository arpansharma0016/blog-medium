from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Confirm, Password, Post, Connect, Me, Draft
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
import random
import math
from django.contrib.auth.hashers import make_password
import os
import json
from django.core import serializers

def register(request):
    
    if request.method == 'POST':
        if not request.POST['first_name']:
            messages.info(request, "Please enter your name!")
            return redirect("register")
        first_name = request.POST['first_name']

        if not request.POST['username']:
            messages.info(request, "Please enter your username!")
            return redirect("register")
        username = request.POST['username']
        
        if not request.POST['password1']:
            messages.info(request, "Please enter your password!")
            return redirect("register")
        password1 = request.POST['password1']
        
        if not request.POST['password2']:
            messages.info(request, "Please enter your password!")
            return redirect("register")
        password2 = request.POST['password2']
        
        if not request.POST['email']:
            messages.info(request, "Please enter your email!")
            return redirect("register")
        email = request.POST['email']
        
        
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect("register")
            
            elif User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect("register")
            
            elif "." in username:
                messages.info(request, 'Username must not contain " . " ')
                return redirect("register")
            
            else:
                for i in username:
                    if i.isupper():
                        messages.info(request, 'Username must be lowercase')
                        return redirect("register")
                        
                    else:
                        if Confirm.objects.filter(username=username).exists():
                            confirm_user = Confirm.objects.get(username=username)
                            confirm_user.delete()
                            digits = "0123456789"
                            otp = ""
                            for i in range(6):
                                otp += digits[math.floor(random.random()*10)]
                            new_otp = otp
                            print(new_otp)
                            confirm_user = Confirm.objects.create(username=username, name=first_name, email=email, password=password1, otp=new_otp)
                            confirm_user.save()
                            subject = 'Thank You for registering to Affiliator!'
                            message = 'Hi ' + confirm_user.name + '!\n \nWe have recieved an Account Creation request from you.\n\nYour Email Confirmation Code is '+new_otp+'.\n\nAt Affiliator, you can easily add Affiliate Products right from your Dedicated Dashboard. Some key features are\n1) No Coding Required\n2) 100% Mobile Responsive\n3) Unlimitted Affiliate Products\n4) Unlimitted Bandwidth\n5) Add Unlimitted Product Categories\n6) Edit any Product Detail\nand many more...\n\nOur Dedicated Management Team is always at your service in case of any Discrepency\nAll the Best\nTeam Affiliator.'
                            from_email = settings.EMAIL_HOST_USER
                            to_list = [confirm_user.email]
                            send_mail(subject, message, from_email, to_list, fail_silently=True)
                            messages.info(request, "An Account Confirmation email has been sent to "+confirm_user.email+". Please Enter the code here.")
                            return redirect("confirm_email", username)
                        else:
                            digits = "0123456789"
                            otp = ""
                            for i in range(6):
                                otp += digits[math.floor(random.random()*10)]
                            new_otp = otp
                            print(new_otp)
                            confirm_user = Confirm.objects.create(username=username, name=first_name, email=email, password=password1, otp=new_otp)
                            confirm_user.save()
                            subject = 'Thank You for registering to Affiliator!'
                            message = 'Hi ' + confirm_user.name + '!\n \nWe have recieved an Account Creation request from you.\n\nYour Email Confirmation Code is '+new_otp+'.\n\nAt Affiliator, you can easily add Affiliate Products right from your Dedicated Dashboard. Some key features are\n1) No Coding Required\n2) 100% Mobile Responsive\n3) Unlimitted Affiliate Products\n4) Unlimitted Bandwidth\n5) Add Unlimitted Product Categories\n6) Edit any Product Detail\nand many more...\n\nOur Dedicated Management Team is always at your service in case of any Discrepency\nAll the Best\nTeam Affiliator.'
                            from_email = settings.EMAIL_HOST_USER
                            to_list = [confirm_user.email]
                            send_mail(subject, message, from_email, to_list, fail_silently=True)
                            messages.info(request, "An Account confirmation email has been sent to "+confirm_user.email)
                            return redirect("confirm_email", username)
        
        else:
            messages.info(request, 'Passwords dont match')
            return redirect("register")
        
    else:
        return render(request, 'register.html')

def confirm_email(request, uname):
    
    if not Confirm.objects.filter(username=uname).exists():
        messages.info(request, "Please register first")
        return redirect("register")
    else:
        confirm_email = Confirm.objects.get(username=uname)
        old_otp = confirm_email.otp
        
        if request.method == 'POST':
            if not request.POST['confirm']:
                messages.info(request, "Please enter the OTP sent to your email address!")
                return redirect("confirm_email", uname)
            otp = request.POST['confirm']
            if otp == old_otp:
                user = User.objects.create_user(username=confirm_email.username, password=confirm_email.password, first_name=confirm_email.name, email=confirm_email.email)
                user.save()
                con = Connect.objects.create(username=confirm_email.username)
                con.save()
                usr = Me.objects.create(user_id=con.id, name=confirm_email.name)
                usr.save()
                confirm_email.delete()
                messages.info(request, "Email confirmed successfully!")
                messages.info(request, "Login to continue.")
                return redirect("login")
            else:
                if confirm_email.attempts < 4:
                    confirm_email.attempts +=1
                    confirm_email.save()
                    messages.info(request, "Incorrect Otp, Try Again.")
                    messages.info(request, str((5-confirm_email.attempts))+ " attempts left.")
                    return redirect("confirm_email", uname)
                else:
                    confirm_email.attempts = 0
                    confirm_email.save()
                    messages.info(request, "Maximum Attempts held for this confirmation code. We've sent a new Confirmation code to "+confirm_email.email+". Please enter the new Code.")
                    return redirect("resend_code", confirm_email.username)

        

        return render(request, "confirm_email_otp.html", {'confirm_email':confirm_email})


def resend_code(request, uname):
    if Confirm.objects.filter(username=uname).exists():
        confirm_user = Confirm.objects.get(username=uname)
        digits = "0123456789"
        otp = ""
        for i in range(6):
            otp += digits[math.floor(random.random()*10)]
        new_otp = otp
        print(new_otp)
        confirm_user.otp = new_otp
        confirm_user.save()
        subject = 'Your new Password Confirmation Code is '+new_otp+'.'
        message = 'Hi ' + confirm_user.name + '!\n \nWe have recieved an Account Creation request from you.\n\nYour New Email Confirmation Code is '+new_otp+'.\n\nAt Affiliator, you can easily add Affiliate Products right from your Dedicated Dashboard. Some key features are\n1) No Coding Required\n2) 100% Mobile Responsive\n3) Unlimitted Affiliate Products\n4) Unlimitted Bandwidth\n5) Add Unlimitted Product Categories\n6) Edit any Product Detail\nand many more...\n\nOur Dedicated Management Team is always at your service in case of any Discrepency\nAll the Best\nTeam Affiliator.'
        from_email = settings.EMAIL_HOST_USER
        to_list = [confirm_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        messages.info(request, "Account confirmation email has been sent to "+confirm_user.email)
        return redirect("confirm_email", uname)
    else:
        messages.info(request, "Please register first!")
        return redirect("register")
    




def login(request):

    if request.GET.get('next'):
        request.session['next'] = request.GET.get('next')
    
    if request.method == 'POST':
        if not request.POST['username']:
            messages.info(request, "Invalid Credentials!")
            return redirect("login")
        username = request.POST['username']
        
        if not request.POST['password']:
            messages.info(request, "Invalid Credentials!")
            return redirect("login")
        password = request.POST['password']
        for i in username:
            if i.isupper():
                messages.info(request, 'Username must be lowercase')
                return redirect("login")
        
        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            confirm_user = User.objects.get(username=username)
            subject = 'New login activity on your Affiliator account!'
            message = 'Hi ' + confirm_user.first_name + '!\n \nHope you are having a great time with Affiliator Affiliate Management Program.\n\nWe have detected a new login activity to your Affiliator Account with following details:-\nDate :- '+datetime.datetime.now().strftime("%d")+' '+datetime.datetime.now().strftime("%B")+' '+datetime.datetime.now().strftime("%Y")+'\nTime :- '+datetime.datetime.now().strftime("%H:%M:%S")+'\n\nHopefully it was you who logged in your Affiliator Affiliate Managemment Account.\n\nIf it was not you, please contact our Management Team to secure your account from fraud.\n\nThank You\nTeam Affiliator' 
            from_email = settings.EMAIL_HOST_USER
            to_list = [confirm_user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            return redirect(request.session['next'])
        
        else:
            messages.info(request, 'Invalid Credentials')
            return redirect('login')
        
    else:
        return render(request, 'login.html')
    

def logout(request):
    auth.logout(request)
    
    return redirect('/')

def forgot_password(request):
    if request.method == "POST":
        if not request.POST['username']:
            messages.info(request, "Please enter your Registered username to continue!")
            return redirect("forgot_password")
        uname = request.POST['username']
        if uname:
            if User.objects.filter(username=uname).exists():
                
                if Password.objects.filter(username=uname).exists():
                    messages.info(request, "We have already sent the confirmation code to the email address associated with "+uname)
                    return redirect("enter_otp", uname)
                else:
                    curr_user = User.objects.get(username=uname)
                    digits = "0123456789"
                    otp = ""
                    for i in range(6):
                        otp += digits[math.floor(random.random()*10)]
                    new_otp = otp
                    print(new_otp)
                    pass_user = Password.objects.create(username=uname, otp=new_otp)
                    pass_user.save()
                    subject = 'Password Reset Request on Affiliator!'
                    message = 'Hi ' + curr_user.first_name + '!\n \nWe have recieved a password reset request on your User Account.\n\nYour Password reset code is ' + pass_user.otp +'\nIf it was not you, then please ignore.\n\nOur dedicated customer support team is always at your service.\nWishing you a happy online journey.\n\nThank You.\nTeam Affiliator'
                    from_email = settings.EMAIL_HOST_USER
                    to_list = [curr_user.email]
                    send_mail(subject, message, from_email, to_list, fail_silently=True)
                    messages.info(request, "Enter the OTP sent to registered email address asssociated with "+uname)
                    return redirect("enter_otp", uname)
            else:
                messages.info(request, "No user with Username " + uname)
                messages.info(request, "Please enter your registered Username")
                return redirect("forgot_password")
        else:
            messages.info(request, "Enter the username")
            return redirect("forgot_password")
    return render(request, "forgot_password.html")

def enter_otp(request, uname):
    if Password.objects.filter(username=uname).exists():
        pass_user = Password.objects.get(username=uname)
        curr_user = User.objects.get(username=uname)
        if request.method == "POST":
            if not request.POST['otp']:
                messages.info(request, "Please enter the OTP sent to your email address to continue!")
                return redirect("enter_otp", uname)
            curr_otp = request.POST['otp']
            if pass_user.otp == curr_otp:
                pass_user.confirmed = True
                pass_user.save()
                messages.info(request, "Email address confirmed")
                return redirect("new_password", uname)
            else:
                if pass_user.attempts < 4:
                    pass_user.attempts += 1
                    pass_user.save()
                    messages.info(request, "Incorrect otp, try again!" +str(5-pass_user.attempts)+" attempts left.")
                    return redirect("enter_otp", uname)
                else:
                    pass_user.attempts = 0
                    pass_user.save()
                    messages.info(request, "Maximum attempts held for this confirmation code. Sending another code to email associated with "+pass_user.username)
                    return redirect("resend_pass_code", uname)
        return render(request, "enter_otp.html", {'pass_user':pass_user})
    else:
        messages.info(request,"Enter the Registered username for which you want to change the Account Password.")
        return redirect("forgot_password")

def new_password(request, uname):
    if Password.objects.get(username=uname):
        pass_user = Password.objects.get(username=uname)
        curr_user = User.objects.get(username=uname)
        if request.method == "POST":
            if not request.POST['password1']:
                messages.info(request, "Please enter the Password to continue!")
                return redirect("enter_otp", uname)
            if not request.POST['password2']:
                messages.info(request, "Please enter the Password to continue!")
                return redirect("enter_otp", uname)
            if pass_user.confirmed:
                password1 = request.POST['password1']
                password2 = request.POST['password2']
                if password1:
                    if password1 == password2:
                        password = make_password(password1, hasher='default')
                        curr_user.password = password
                        pass_user.delete()
                        curr_user.save()
                        messages.info(request, "Password changed successfully.")
                        return redirect("login")
                    else:
                        messages.info(request, "Passwords Don't Match. Please re-enter the Passwords.")
                        return redirect("new_password")
                else:
                    messages.info(request, "Password Fields cannot be blank.")
                    return redirect("new_password")
            else:
                messages.info(request, "Please enter your username registered with Affiliator")
                return redirect("forgot_password")
        return render(request, "new_password.html")
    else:
        messages.info(request, "Please enter your username registered with Affiliator")
        return redirect("forgot_password")

def resend_pass_code(request, uname):
    if Password.objects.filter(username=uname).exists():
        curr_user = User.objects.get(username=uname)
        pass_user = Password.objects.get(username=uname)
        digits = "0123456789"
        otp = ""
        for i in range(6):
            otp += digits[math.floor(random.random()*10)]
        new_otp = otp
        print(new_otp)
        pass_user.otp = new_otp
        pass_user.save()
        subject = 'Password Reset Request on Affiliator!'
        message = 'Hi ' + curr_user.first_name + '!\n \nWe have recieved a password reset request on your User Account.\n\nYour Password reset code is ' + pass_user.otp +'\nIf it was not you, then please ignore.\n\nOur dedicated customer support team is always at your service.\n Wishing you a happy online journey.\n\nThank You.\nTeam Affiliator'
        from_email = settings.EMAIL_HOST_USER
        to_list = [curr_user.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        messages.info(request, "Password reset code has been sent to email address associated with "+uname)
        return redirect("enter_otp", uname)
    else:
        messages.info(request, "Please enter the username first")
        return redirect("forgot_password")

def me(request):
    if request.user.is_authenticated:
        con = Connect.objects.filter(username=request.user.username).first()
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
        if request.method == "POST":
            name = request.POST['name']
            bio = request.POST['bio']
            usr.name = name
            usr.bio = bio

            if request.FILES.get('image'):
                image = request.FILES['image']
                usr.image = image
            usr.save()

        context = {
            'con':con,
            'usr':usr,
            'posts':posts,
        }
        return render(request, "me.html", context)

    else:
        request.session['next'] = "me"
        messages.info(request, "You need to Login First!")
        return redirect("login")
    

def delete_image(request):
    if request.user.is_authenticated:
        con = Connect.objects.filter(username=request.user.username).first()
        if not con:
            request.session['next'] = "write"
            messages.info(request, "You need to Login First!")
            return redirect("login")

        usr = Me.objects.filter(user_id=con.id).first()
        if not usr:
            request.session['next'] = "write"
            messages.info(request, "You need to Login First!")
            return redirect("login")
            
        if usr.image:
            usr.image.delete(save=True)
        return redirect("me")
    
    else:
        request.session['next'] = "me"
        messages.info(request, "You need to Login First!")
        return redirect("login")



@csrf_exempt
def write(request):
    if request.user.is_authenticated:
        con = Connect.objects.filter(username=request.user.username).first()
        usr = Me.objects.filter(user_id=con.id).first()

        if request.method == "POST":
            updatedData=json.loads(request.body.decode('UTF-8'))
            po = Post.objects.create(user_id=con.id)
            if updatedData['title']:
                title = updatedData['title']
                po.title = title
            else:
                messages.info(request, "Please provide a title for the post!")
                return redirect("write")
            
            if updatedData['caption']:
                caption = updatedData['caption']
                po.caption = caption

            if updatedData['post_html']:
                post = updatedData['post_html']
                po.post = post
            else:
                messages.info(request, "Post cannot be blank!")
                return redirect("write")

            if updatedData['post_json']:
                post_json = updatedData['post_json']
                po.post_json = post_json
            else:
                messages.info(request, "Post cannot be blank!")
                return redirect("write")

            if updatedData['thumbnail']:
                thumbnail = updatedData['thumbnail']
                po.thumbnail = thumbnail

            if updatedData['tags']:
                tags = updatedData['tags'].strip()
                str = ""
                t = tags.split(" ")
                ttt = list()
                x = 0
                for tt in t:
                    if tt not in ttt:
                        if x <= 5:
                            ttt.append(tt)
                            x += 1
                for s in ttt:
                    str += s + " "
                po.tags = str.strip()
            
            po.save()
            return JsonResponse({'status':'success', 'po':po.post_json})

        context = {
            'con':con,
            'usr':usr
        }
        return render(request, "write.html", context)

    else:
        request.session['next'] = "write"
        messages.info(request, "You need to Login First!")
        return redirect("login")


def delete_post(request, post_id):
    if request.user.is_authenticated:
        con = get_object_or_404(Connect, username=request.user.username)
        usr = get_object_or_404(Me, user_id=con.id)
        po = get_object_or_404(Post, id=post_id)
        if po.user_id == con.id:
            po.delete()
            return redirect("me")
        else:
            return redirect("me")
        
    else:
        request.session['next'] = "write"
        messages.info(request, "You need to Login First!")
        return redirect("login")