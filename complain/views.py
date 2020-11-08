from django.shortcuts import render, redirect
from .models import Complain, Feedback
from cart.models import Order
from datetime import datetime


# Create your views here.

# ------------- complain admin ------------------------------------------
def adminViewComplain(request):
    viewComplainList = Complain.objects.filter(complainStatus='pending')
    return render(request, 'admin/viewComplain.html', {'viewComplainList': viewComplainList})


def adminComplainreply(request):
    id = request.GET['id']
    getcomplain = Complain.objects.get(pk=id)
    return render(request, 'admin/reply.html', {'getcomplain': getcomplain})


def adminInsertreply(request):
    id = request.POST['id']
    replysub = request.POST['replysub']
    replymsg = request.POST['replymsg']

    reply = Complain.objects.get(pk=id)
    reply.replySubject = replysub
    reply.replyMessage = replymsg
    reply.replyDate = datetime.today().date()
    reply.replyTime = datetime.today().time()
    reply.complainStatus = "reply"
    reply.save()
    return redirect('/admin/viewComplain')


# ---------------------- comaplain user -------------------------------


def loadComplain(request):
    return render(request, 'user/addComplain.html')


def insertComplain(request):
    subject = request.POST['subject']
    description = request.POST['description']

    addComplain = Complain(complainSubject=subject, complainDescription=description,
                           complainTo_LoginId_id=request.session['login_Id'], complainStatus='pending')
    addComplain.save()

    return redirect('/viewComplain')


def viewComplain(request):
    viewComplainList = Complain.objects.filter(complainTo_LoginId=request.session['login_Id'])
    return render(request, 'user/viewComplain.html', {'viewComplainList': viewComplainList})


def deleteComplain(request):
    id = request.GET['id']

    deleteComplain = Complain.objects.get(pk=id)
    deleteComplain.delete()
    return redirect('/viewComplain')


# -------------------------- feedback user ----------------------------------------------------

def loadfeedback(request):
    productId = request.GET['productId']
    orderId = request.GET['orderId']
    return render(request, 'user/addFeedback.html', {'productId': productId,'orderId':orderId})


def insertFeedback(request):
    rating = request.POST['feedbackRating']
    description = request.POST['description']
    productId = request.POST['productId']
    orderId = request.POST['orderId']

    getOrder = Order.objects.get(pk=orderId)
    product = eval(getOrder.product)
    product[productId]['feedback'] = 'yes'
    getOrder.product = product
    getOrder.save()

    addFeedback = Feedback(rating=rating, feedback=description, feedbackTo_LoginId_id=request.session['login_Id'],
                           productId_id=productId)
    addFeedback.save()

    return redirect('/viewOrder')

def viewFeedback(request):
    getFeedbackList = Feedback.objects.filter(feedbackTo_LoginId_id=request.session['login_Id'])
    return render(request,'user/viewFeedback.html',{'getFeedbackList':getFeedbackList})

#----------------- feedback admin ------------------------

def adminViewFeedback(request):

    viewFeedbackList = Feedback.objects.all()

    return render(request,'admin/viewFeedback.html',{'viewFeedbackList':viewFeedbackList})
