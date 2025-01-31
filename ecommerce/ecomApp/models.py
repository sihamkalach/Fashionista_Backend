from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.db.models.fields import BLANK_CHOICE_DASH

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True, blank=True ,upload_to='categories-images/')
    def __str__(self):
        return self.name


class Product(models.Model):
    # Basic information
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    description = models.TextField()
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
    stock = models.CharField(max_length=255)
    # images
    image = models.ImageField(null=True, blank=True)

    # User association
    user = models.ForeignKey(User, related_name="products", on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Review(models.Model):
    product = models.ForeignKey(Product, related_name="reviews", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    # Link to User for reviewer
    reviewer = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.rating)

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    paymentMethod = models.CharField(max_length=200,null=True,blank=True)
    taxPrice = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    shippingPrice = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    totalPrice = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    isPaid = models.BooleanField(default=False)
    paidAt = models.DateTimeField(auto_now_add=False,null=True, blank=True)
    isDeliver = models.BooleanField(default=False)
    deliveredAt = models.DateTimeField(auto_now_add=False,null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    _id =  models.AutoField(primary_key=True,editable=False)

    def __str__(self):
        return str(self.createdAt)


class OrderItem(models.Model):
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    order  = models.ForeignKey(Order,on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=200,null=True,blank=True)
    qty = models.IntegerField(null=True,blank=True,default=0)
    price = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    image = models.CharField(max_length=200,null=True,blank=True)
    _id =  models.AutoField(primary_key=True,editable=False)

    def __str__(self):
        return str(self.name)



class ShippingAddress(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE,null=True,blank=True)
    address = models.CharField(max_length=200,null=True,blank=True)
    city  = models.CharField(max_length=200,null=True,blank=True)
    postalCode = models.CharField(max_length=200,null=True,blank=True)
    country = models.CharField(max_length=200,null=True,blank=True)
    shippingPrice = models.DecimalField(max_digits=12,decimal_places=2,null=True,blank=True)
    _id = models.AutoField(primary_key=True,editable=False)

    def __str__(self):
        return str(self.address)