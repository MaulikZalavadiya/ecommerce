from django.db import models
from login.models import Loginmaster


# Create your models here.

# class Payment(models.Model):
#     payment = models.IntegerField()
#     paymentstatus = models.CharField(max_length=50)
#     orders = models.CharField(max_length=100)
#     userId = models.ForeignKey(Loginmaster, on_delete=models.CASCADE, db_column='userId', null=True)
