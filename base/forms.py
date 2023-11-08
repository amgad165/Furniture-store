from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser , ContactMessage, Product


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email','phone_number')



class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['first_name', 'last_name', 'email', 'phone_number','message']





class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'length', 'width', 'depth', 'price', 'category', 'main_image', 'color']