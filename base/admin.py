from django.contrib import admin
from . models import *
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(Colour)
admin.site.register(ProductImages)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(ProductTracking)
admin.site.register(CategoryTracking)
admin.site.register(ContactMessage)