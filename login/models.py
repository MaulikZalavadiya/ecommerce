from django.db import models


# Create your models here.

class Loginmaster(models.Model):
    loginUserName = models.CharField(max_length=100, null=False)
    loginEmail = models.CharField(max_length=100, null=False)
    loginMobileNo = models.CharField(max_length=100, null=True, blank=True)
    loginPassword = models.CharField(max_length=50, null=False)
    loginRole = models.CharField(max_length=50, null=False)
    loginCreatedAt = models.DateField(auto_now_add=True)
    loginStatus = models.CharField(max_length=50, null=False)


class OTPmaster(models.Model):
    mobileOTP = models.IntegerField()
    emailOTP = models.CharField(max_length=10)
    login_Id = models.ForeignKey(Loginmaster, on_delete=models.CASCADE, db_column='login_Id')
