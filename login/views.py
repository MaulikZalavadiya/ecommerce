from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from django.http import HttpResponse
from .models import Loginmaster, OTPmaster
import random
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib.auth.base_user import BaseUserManager
from twilio.rest import Client
from django.contrib.sessions.models import Session


# Create your views here.
def generateOTP(email, mobileNumbaer):
    OTP_list = []
    mobileOTP = random.randint(100000, 999999)
    account_sid = "AC89c39362b649bb9d1bb3c8e98de26bae"
    auth_token = "6fe185b97904d41e6f8729052b178390"
    client = Client(account_sid, auth_token)
    client.messages.create(to="+91" + str(mobileNumbaer), from_="+12055707697",
                           body="this is eshopper OTP" + str(mobileOTP))
    OTP_list.append(mobileOTP)

    emailOTP = str(BaseUserManager().make_random_password(8))
    print("loginPassword=" + emailOTP)
    sender = "p2ploans2020@gmail.com"
    receiver = email
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = "ChitChat Password"
    msg.attach(MIMEText(emailOTP, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, "finelyear2020")
    text = msg.as_string()
    server.sendmail(sender, receiver, text)
    OTP_list.append(emailOTP)

    return OTP_list


def loadLogin(request):
    return render(request, 'user/login.html')


def insertRegister(request):
    name = request.POST['name']
    email = request.POST['email']
    mobileNumber = request.POST['mobileNumber']
    password = request.POST['password']
    role = 'user'
    action = 'active'

    varify = Loginmaster.objects.filter(loginEmail=email) or Loginmaster.objects.filter(loginMobileNo=mobileNumber)

    if len(varify) == 0:
        insertLoginQuert = Loginmaster(loginUserName=name, loginEmail=email, loginMobileNo=mobileNumber,
                                       loginPassword=password, loginRole=role, loginStatus='active')
        insertLoginQuert.save()

        OTP_list = generateOTP(email, mobileNumber)
        insertOTP = OTPmaster(mobileOTP=OTP_list[0], emailOTP=OTP_list[1], login_Id=insertLoginQuert)
        insertOTP.save()

        obj = Loginmaster.objects.filter(loginEmail=email, loginMobileNo=mobileNumber)
        login_Id = obj[0].pk

        return render(request, 'user/addOTP.html', {'loginId': login_Id})
    else:
        return render(request, 'user/login.html',
                      {'alreadyExist': 'this Email address or mobile number is alresy exist, please try other.'})


def insertLogin(request):
    email = request.POST['email']
    password = request.POST['password']

    varify = Loginmaster.objects.filter(loginEmail=email, loginPassword=password)

    if len(varify) != 0:
        request.session['login_Id'] = varify[0].id
        request.session['login_UserName'] = varify[0].loginUserName
        request.session['login_Email'] = varify[0].loginEmail
        request.session['login_Role'] = varify[0].loginRole
        request.session['login_MobileNO'] = varify[0].loginMobileNo
        if request.session['login_Role'] == 'user':
            return redirect('/')
        if request.session['login_Role'] == 'admin':
            return redirect('/admin/loadDashbord')
    else:
        return render(request, 'user/login.html', {'notValid': 'Email or Password is not valid.'})


def valideOTP(request):
    mobileOTP = request.POST['mobileOTP']
    emailOTP = request.POST['emailOTP']
    loginId = request.POST['loginId']

    obj = OTPmaster.objects.filter(login_Id=loginId)
    print(">>>>>>>>>>>>>>>>>", obj[0].mobileOTP, ">>>>>>>>>>>>>.", obj[0].emailOTP)

    if str(obj[0].mobileOTP) == str(mobileOTP) and str(obj[0].emailOTP) == str(emailOTP):
        deleteOTP = OTPmaster.objects.get(login_Id=loginId)
        deleteOTP.delete()
        return render(request, 'user/login.html', {'successfulyRegister': 'you are successfully registered.'})
    else:
        return render(request, 'user/addOTP.html', {'invalidOTP': 'please enter valid OTP.', 'loginId': loginId})


def logout(request):
    request.session.clear()
    return redirect("/")
