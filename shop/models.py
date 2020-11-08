from django.db import models
from cart.models import Coupon

# Create your models here.


class Category(models.Model):
    category = models.CharField(max_length=50, null=True)
    # coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, db_column='coupon', null=True)
    status = models.CharField(max_length=50, null=True)


class Subategory(models.Model):
    subcategory = models.CharField(max_length=50, null=True)
    categoryId = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='categoryId', null=True)
    status = models.CharField(max_length=50, null=True)
    # coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, db_column='coupon', null=True)

    def as_dict(self):
        return {
            'id': self.id,
            'subcategory': self.subcategory,
            'categoryId': self.categoryId_id,
            'status': self.status
        }


class Type(models.Model):
    type = models.CharField(max_length=50, null=True)
    subcategoryId = models.ForeignKey(Subategory, on_delete=models.CASCADE, db_column='subcategoryId', null=True)
    categoryId = models.ForeignKey(Category, on_delete=models.CASCADE, db_column='categoryId', null=True)
    # coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, db_column='coupon', null=True)
    status = models.CharField(max_length=50, null=True)


class Product(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    # image = models.ImageField(upload_to="product", editable=True)
    image = models.CharField(max_length=5000, null=True)
    color = models.CharField(max_length=50)
    category = models.CharField(max_length=50)
    subcategory = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length=300)
    # promocode = models.CharField(max_length=100, null=True)
    size = models.CharField(max_length=100, null=True)
    quantity = models.CharField(max_length=100,null=True)
    pub_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=100)
    coupon = models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.name


class Contact(models.Model):
    msg_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=70, default="")
    phone = models.CharField(max_length=70, default="")
    desc = models.CharField(max_length=500, default=0)

    def __str__(self):
        return self.name


class Wishlist(models.Model):
    wishProductId = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='wishProductId')
    userId = models.IntegerField()


class Benner(models.Model):
    image = models.ImageField(upload_to="benner", editable=True)
    link = models.CharField(max_length=1000, null=True, blank=True)
    contact = models.CharField(max_length=13, null=True, blank=True)
    rank = models.IntegerField()
    status = models.CharField(max_length=50, null=True)
