from django.db.models import fields
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *


class UserSerializer(serializers.ModelSerializer):
    name= serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User 
        fields = '__all__'

    def get__id(self,obj):
        return obj.id

    def get_isAdmin(self,obj):
        return obj.is_staff

    def get_name(self,obj):
        name = obj.first_name
        if name=="":
            name = obj.email
        return name

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'created_at', 'updated_at','image']
class ReviewSerializer(serializers.ModelSerializer):
    reviewerName = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id', 'product', 'rating', 'comment', 'date', 'reviewerName']

    def get_reviewerName(self, obj):
        return obj.reviewer.username 
class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(read_only= True)
    class Meta:
        model = Product 
        fields = '__all__'
    def get_reviews(self, obj):
        reviews = obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    orderItems = serializers.SerializerMethodField(read_only=True)
    shippingAddress = serializers.SerializerMethodField(read_only=True)
    User = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_orderItems(self,obj):
        items = obj.orderitem_set.all()
        serializer = OrderItemSerializer(items,many=True)
        return serializer.data

    def get_shippingAddress(self,obj):
        try:
            address = ShippingAddressSerializer(obj.shippingaddress,many=False).data
        except:
            address = False
        return address

    def get_User(self,obj):
        items = obj.user
        serializer = UserSerializer(items,many=False)
        return serializer.data



