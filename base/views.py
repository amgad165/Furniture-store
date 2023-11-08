from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from . models import *
from django.db.models import Count
from django.db.models import Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm , ContactMessageForm,ProductForm
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import F
from django.db.models import Count

# Create your views here.
def home(request):
    success_message = None

    if request.method == 'POST':
        
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            success_message = "Your message has been saved successfully, we will reach you soon"
           
    else:
        form = ContactMessageForm()
    return render(request,"index.html", {'form': form,'success_message':success_message})



def signup(request):
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request, user)
            return redirect('home')  # Change 'home' to the URL name of your home page
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def shop(request, category):
    # Start with all products that match the selected category
    products = Product.objects.filter(category=category)

    if not request.user.is_superuser:
        #user tracking section
        category_name = category  
        # Get or create category tracking object
        category_tracking, created = CategoryTracking.objects.get_or_create(category=category_name)
        # Increment counts for category 
        category_tracking.counts += 1
        category_tracking.save()





    # Get the selected colors from the form
    colors = request.GET.getlist('colors')

    # Get the lowest and highest prices from the form
    lowest_price_form = request.GET.get('min_price')
    highest_price_form = request.GET.get('max_price')

    # Apply additional filters based on colors
    if colors:
        products = products.filter(color__name__in=colors)

    # Apply additional filters based on prices
    if lowest_price_form:
        lowest_price_form = float(lowest_price_form.replace(' EGP', ''))
        products = products.filter(price__gte=lowest_price_form)
    if highest_price_form:
        highest_price_form = float(highest_price_form.replace(' EGP', ''))
        products = products.filter(price__lte=highest_price_form)

    # Get the lowest and highest prices for the filtered products
    lowest_price = products.aggregate(Min('price'))['price__min']
    highest_price = products.aggregate(Max('price'))['price__max']

    # Paginate the filtered products
    page = request.GET.get('page')
    paginator = Paginator(products, 12)  # 20 products per page
    try:
        paginated_products = paginator.page(page)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    # Get all available colors related to the filtered products and their counts
    color_counts = Colour.objects.filter(product__in=products).annotate(count=Count('product'))
    products_count = products.count()

    context = {
        "products": paginated_products,
        "category": category,
        "color_counts": color_counts,
        'lowest_price': lowest_price,
        'highest_price': highest_price,
        "products_count": products_count,
    }

    return render(request, "shopping.html", context)




def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_superuser: 
    
        product_tracking, created = ProductTracking.objects.get_or_create(product=product)
        product_tracking.counts += 1
        product_tracking.save()


    context = {'product': product}
    return render(request, 'product_details.html', context)


def add_colors(request):
    success_message = None
    error_message = None
    if request.method == 'POST':
        colour_name = request.POST.get('colour_name')
        colour_hex = request.POST.get('colour_hex')
        try:
            colour = Colour(name=colour_name,hex_code =colour_hex )
            colour.save()
            success_message = "Colour Added successfully"
        except:
            error_message = "Failed to Upload Colour , please try again"

    return render(request,"settings/add_colors.html",{"success_message":success_message,"error_message":error_message})

# @api_view(['POST'])
@login_required
def add_to_cart(request):
    id = request.data.get('id', None)
    qty = int(request.data.get('qty', None))
    email = request.user.email

    current_user = get_object_or_404(CustomUser, email=email)

    
    product = get_object_or_404(Product, id=id)

    order_item_qs = OrderItem.objects.filter(
        product=product,
        user=current_user,
        ordered=False
    )


    if order_item_qs.exists():
        order_item = order_item_qs.first()
        if qty:
            order_item.quantity += qty
        else:
            order_item.quantity += 1
        order_item.save()
    else:
        if qty:
            order_item = OrderItem.objects.create(
            product=product,
            user=current_user,
            ordered=False,
            quantity=qty
            )           
        else:
            order_item = OrderItem.objects.create(
                product=product,
                user=current_user,
                ordered=False
            )
        order_item.save()

    order_qs = Order.objects.filter(user=current_user, ordered=False)
    
    if order_qs.exists():
        
        order = order_qs[0]
        if not order.items.filter(product__id=order_item.id).exists():
            
            order.items.add(order_item)

            cart_items = order.items.all()
            total_items = len(cart_items)
            total_quantity = sum(item.quantity for item in cart_items)

            return Response({'success': 'order updated successfully',"cart_items_count":total_quantity}, status=status.HTTP_201_CREATED)
        else:
            
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)



    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=current_user, ordered_date=ordered_date)
        order.items.add(order_item)

        cart_items = order.items.all()
        total_items = len(cart_items)
        total_quantity = sum(item.quantity for item in cart_items)

        return Response({'success': 'added to cart successfully',"cart_items_count":total_quantity}, status=status.HTTP_201_CREATED)


@login_required
def cart(request):
    user = request.user  # Get the currently logged-in user
    try:
        order = Order.objects.get(user=user, ordered=False)
        order_items = order.items.all()
        cart_count = len(order.items.all())
        
        # get total orders 
        total_price = order.get_total()





        return render(request, "cart.html", {'order_items': order_items,'total_price':total_price,"cart_count":cart_count})

    except Order.DoesNotExist:
        # Handle the case where the order doesn't exist
        order_items = None    
        return render(request, "cart.html", {'order_items': order_items})







def update_cart(request):
    if request.method == "POST":
        # Process the data sent by the "Update Cart" button
        product_ids = request.POST.getlist('product_id')
        
        quantities = request.POST.getlist('quantity')  # These are the updated quantities
        
        current_user = request.user
        # Loop through the product IDs and quantities to update the cart
        for product_id, quantity in zip(product_ids, quantities):
            product = get_object_or_404(Product, id=product_id)
            quantity = int(quantity)  # Convert the quantity to an integer

            cart = OrderItem.objects.get(user=current_user,product__id=product_id,ordered=False)
            cart.quantity = quantity
            
            cart.save()
        
        # Return a JSON response to indicate success (you can customize this)
        
        return redirect("cart")

    # Handle GET requests (if needed)
    return JsonResponse({"message": "Invalid request"}, status=400)

@login_required
def remove_item(request):
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        
        # Delete the OrderItem
        order_item = OrderItem.objects.filter(
            product__id=product_id,
            user=request.user,
            ordered=False
        ).first()
        
        if order_item:
            order_item.delete()
        
        order = Order.objects.get(user=request.user, ordered=False) 
        if order:
            # Calculate the updated total price
            updated_total_price = float(order.get_total())
            
            cart_items = order.items.all()
            
            total_quantity = sum(item.quantity for item in cart_items)
        
            # Return the updated total price as JSON response
            return JsonResponse({'total_price': updated_total_price,"cart_items_count":total_quantity})
        
    return JsonResponse({'message': 'Invalid request'}, status=400)

@login_required
def confirm_order(request):
    current_user = request.user
    try:
        order = Order.objects.get(user=current_user, ordered=False)
        order_items = order.items.all()
        
        order_items.update(ordered=True)
        for item in order_items:
            item.save()

        order.ordered = True
        order.save()

        return redirect('orders')  
    
    except Exception as e:
        # send an email to ourselves
        return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)


@login_required
def orders(request):
    user = request.user  # Get the currently logged-in user

    try:
        orders = Order.objects.filter(user=user, ordered=True)

        return render(request, "orders.html", {'orders': orders})

    except Order.DoesNotExist:
        # Handle the case where the order doesn't exist
        orders = None    
        return render(request, "orders.html", {'orders': orders})

@login_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Use a transaction to ensure that either both the order and items are deleted or none
        with transaction.atomic():
            # Delete related items
            order.items.all().delete()

            # Delete the order
            order.delete()

        return redirect('orders')



def analysis(request):
    # Retrieve data from CategoryTracking and ProductTracking models
    category_data = CategoryTracking.objects.values('category', 'counts')
    product_data = ProductTracking.objects.values('product__name', 'counts').order_by('-counts')[:20]

    # Extract category names and counts
    category_names = [item['category'] for item in category_data]
    category_counts = [item['counts'] for item in category_data]

    # Extract product names and counts
    product_names = [item['product__name'] for item in product_data]
    product_counts = [item['counts'] for item in product_data]



    ordered_data = Product.objects.filter(orderitem__ordered=True)\
                                  .annotate(total_ordered=Coalesce(Sum('orderitem__quantity'), 0))\
                                  .values('name', 'total_ordered')\
                                  .annotate(num_orders=Count('orderitem__order__id'))\
                                  .order_by('-num_orders')[:10]

    # Extract product names, total quantities, and order counts
    product_ordered = [item['name'] for item in ordered_data]
    total_quantities = [item['total_ordered'] for item in ordered_data]

    # Return the lists in the context
    return render(request, 'settings/analysis.html', {
        'category_names': category_names,
        'category_counts': category_counts,
        'product_names': product_names,
        'product_counts': product_counts,
        'product_ordered':product_ordered,
        
        'total_quantities' : total_quantities
    })

def orders_handling(request):
    if request.method == 'POST':
        for order in Order.objects.all():
            order_id = order.id
            delivered_key = f'delivered_{order_id}'
            received_key = f'received_{order_id}'
            if delivered_key in request.POST:
                order.being_delivered = True

            if received_key in request.POST:
                order.received = True
            else:
                order.received = False

            order.save()
        return redirect('orders_handling')

    orders = Order.objects.filter(being_delivered=False).order_by('received')


    return render(request, 'settings/orders_handling.html', {'orders': orders})



def add_product(request):
    error_message = None
    success_message = None
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the product details
            product = form.save()
            success_message = "Product added successfully"

            # Save multiple images
            images = request.FILES.getlist('images')
            for image in images:
                product_image = ProductImages(product=product, image=image)
                product_image.save()
                
        else:
            error_message = "Error adding product"

    else:
        form = ProductForm()

    return render(request, 'settings/add_product.html', {'form': form,'success_message':success_message,'error_message':error_message})

def add_product_images(request):
    error_message = None
    success_message = None
    if request.method == 'POST':
        product_id = request.POST.get('product')
        images = request.FILES.getlist('images')

        # Validate the product and uploaded images
        if not images:
            error_message = "Error "
        try:
            product = Product.objects.get(pk=product_id)
            # Create ProductImages objects for each uploaded image and associate them with the product
            for image in images:
                product_image = ProductImages(product=product, image=image)
                product_image.save()
                success_message = "Upload Success"
        except: 
            error_message = "Error , please try again later"
 
    # Fetch the list of available products for rendering in the template
    products = Product.objects.all()

    return render(request, 'settings/add_product_images.html', {'products': products,"error_message":error_message,"success_message":success_message})



def messages(request):
    # Get all messages sorted by date in descending order (newest first)
    messages = ContactMessage.objects.order_by('-date')

    # Set the number of messages to display per page
    messages_per_page = 10

    # Paginate the messages
    page = request.GET.get('page')
    paginator = Paginator(messages, messages_per_page)

    try:
        messages = paginator.page(page)
    except PageNotAnInteger:
        messages = paginator.page(1)
    except EmptyPage:
        messages = paginator.page(paginator.num_pages)

    return render(request, 'settings/messages.html', {'messages': messages})


def about_us(request):


    return render(request,"about.html")

def contact_us(request):


    return render(request,"contact.html")