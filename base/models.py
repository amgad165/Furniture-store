from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from PIL import Image
from django.utils.translation import gettext as _

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255,null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.email




class Product(models.Model):
    category_CHOICES = [
        ('living', 'living'),
        ('dining', 'dining'),
        ('bedrooms', 'bedrooms'),
        ('offices', 'offices'),
        ('kitchens', 'kitchens'),
        ('dressing', 'dressing'),
        ('chairs', 'chairs'),
        ('hangings', 'hangings'),
        ('accessories', 'accessories'), 
        ('tables', 'tables'), 
        ('doors', 'doors'),
        ('paravans', 'paravans'), 
  
        ]
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    length = models.CharField(max_length=255,null=True,blank=True)
    width = models.CharField(max_length=255,null=True,blank=True)
    depth = models.CharField(max_length=255,null=True,blank=True)

    price = models.FloatField(null=True, blank=True)
    category = models.CharField(max_length=255,choices=category_CHOICES)
    
    main_image = models.FileField(upload_to='product_images/') 
    color = models.ForeignKey('Colour',on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return self.name
    

    def save(self):
        super().save()  # saving image first

        img = Image.open(self.main_image.path) # Open image using self
        print(img.height)
        print(img.width)
        if img.height > 866 or img.width > 1154:
            new_img = (1080, 1080)
            img.thumbnail(new_img)
            img.save(self.main_image.path)  # saving image at the same path
    

class ProductImages(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='product_images/')

    def __str__(self):
        return str(self.product) + ' - ' +str(self.image).split('/')[1]

    def save(self):
            super().save()  # saving image first

            img = Image.open(self.image.path) # Open image using self
            print(img.height)
            print(img.width)
            if img.height > 866 or img.width > 1154:
                new_img = (1080, 1080)
                img.thumbnail(new_img)
                img.save(self.image.path)  # saving image at the same path


class Colour(models.Model):

    name = models.CharField(max_length=255,unique=True)
    hex_code = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    





class OrderItem(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"

    def get_total_item_price(self):
        return self.quantity * self.product.price

class Order(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)



    def __str__(self):
        return self.user.email

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()

        return total
    

class CategoryTracking(models.Model):
    category = models.CharField(max_length=100, unique=True)
    counts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.category

class ProductTracking(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    counts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.product)


class ContactMessage(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=100)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True,null=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"



