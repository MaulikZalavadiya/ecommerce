from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from login.models import Loginmaster
# from shop.models import Product
from myprofile.models import Address


# from payment.models import Payment


# Create your models here.

# class Order(models.Model):
#     orderproductId = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='orderproductId')
#     Quantity = models.IntegerField(default=1)
#     totalPrice = models.IntegerField()
#     orderDate = models.DateField(auto_now_add=True)
#     delhiveryDate = models.DateField()
#     status = models.CharField(max_length=50, null=False)
#     userId = models.ForeignKey(Loginmaster, on_delete=models.CASCADE, db_column='userId')
#     address = models.ForeignKey(Address, on_delete=models.CASCADE, db_column='address', null=True)
#     paymentId = models.ForeignKey(Payment, on_delete=models.CASCADE, db_column='paymentId', null=True)

class Order(models.Model):
    product = models.CharField(max_length=5000, null=True)
    totalPrice = models.FloatField()
    orderDate = models.DateField(null=True)
    delhiveryDate = models.DateField(null=True)
    orderstatus = models.CharField(max_length=50, null=True)
    anyReturn = models.CharField(max_length=50, null=True)
    paymentstatus = models.CharField(max_length=50, null=True)
    txnId = models.CharField(max_length=500, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, db_column='address', null=True)
    userId = models.ForeignKey(Loginmaster, on_delete=models.CASCADE, db_column='userId')

class Coupon(models.Model):
    code = models.CharField(max_length=50,unique=True)
    valid_from=models.DateField()
    valid_to = models.DateField()
    discount = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    perameter=models.CharField(max_length=50,null=True)
    category = models.CharField(max_length=100,null=True)
    subcategory = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=50)
