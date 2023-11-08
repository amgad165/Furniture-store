"""
URL configuration for salem_arts_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from base import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home,name='home'),
    path('signup/', views.signup, name='signup'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('shop/<str:category>/', views.shop, name='shop'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('remove_item/', views.remove_item, name='remove_item'),

    path('confirm_order/', views.confirm_order, name='confirm_order'),
    path('orders/', views.orders, name='orders'),
    path('delete_order/<int:order_id>/', views.delete_order, name='delete_order'),


    path('settings', views.add_colors,name='add_colors'),
    path('analysis', views.analysis,name='analysis'),
    path('orders_handling', views.orders_handling,name='orders_handling'),
    path('add_product_images', views.add_product_images,name='add_product_images'),
    path('add_product', views.add_product,name='add_product'),
    path('messages', views.messages,name='messages'),

    path('about_us', views.about_us,name='about_us'),
    path('contact_us', views.contact_us,name='contact_us'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
