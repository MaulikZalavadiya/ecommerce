from django.db import models
from login.models import Loginmaster


# Create your models here.


class Address(models.Model):
    fullName = models.CharField(max_length=100, null=False)
    mobileNo = models.CharField(max_length=100)
    alternetMobileNo = models.CharField(max_length=100, null=True, blank=True)
    PINCode = models.IntegerField()
    home = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=1000, null=False)
    landmark = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=100, null=False)
    state = models.CharField(max_length=100, null=False)
    country = models.CharField(max_length=100, null=False)
    action = models.CharField(max_length=100, null=False)
    login_Id = models.ForeignKey(Loginmaster, on_delete=models.CASCADE, db_column='login_Id')
