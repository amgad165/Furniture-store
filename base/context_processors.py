from base.models import Order, OrderItem  # Import your Order and OrderItem models

def cart_count(request):
    if request.user.is_authenticated:
        # Get the cart for the logged-in user
        cart = Order.objects.filter(user=request.user, ordered=False).first()

        if cart:
            # Calculate the total number of items and their quantities in the cart
            cart_items = cart.items.all()
            total_quantity = sum(item.quantity for item in cart_items)
        else:
            total_quantity = 0
    else:
        total_quantity = 0

    return {'total_quantity': total_quantity}