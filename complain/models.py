from django.db import models
from login.models import Loginmaster
from shop.models import Product


# Create your models here.

class Complain(models.Model):
    complainSubject = models.CharField(max_length=500)
    complainDescription = models.CharField(max_length=5000)
    complainDate = models.DateField(auto_now_add=True)
    complainTime = models.TimeField(auto_now_add=True)
    complainStatus = models.CharField(max_length=50)
    complainTo_LoginId = models.ForeignKey(Loginmaster, on_delete=models.CASCADE, related_name='complainTo_LoginId',
                                           null=True)
    complainFrom_LoginId = models.ForeignKey(Loginmaster, on_delete=models.CASCADE, related_name='complainFrom_LoginId',
                                             null=True)
    replySubject = models.CharField(max_length=500)
    replyMessage = models.CharField(max_length=5000)
    replyDate = models.DateField(null=True)
    replyTime = models.TimeField(null=True)


class Feedback(models.Model):
    feedback = models.CharField(max_length=5000)
    feedbackDate = models.DateField(auto_now_add=True)
    feedbackTime = models.TimeField(auto_now_add=True)
    rating = models.IntegerField()
    productId = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productId', null=True)
    feedbackTo_LoginId = models.ForeignKey(Loginmaster, on_delete=models.CASCADE, related_name='feedbackTo_LoginId',
                                           null=True)
