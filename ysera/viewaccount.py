from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import OrderItem, ProductImage
from django.db.models import Prefetch
from django.shortcuts import redirect, get_object_or_404
from .models import CartItem
from django.shortcuts import render, redirect, get_object_or_404,HttpResponse
from .models import Cart, CartItem
from .models import Product,UserProfile
from .models import Order
from .models import OrderItem

def account_detail(request):
    if not request.user.is_authenticated:
        return redirect("login")
    
    
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    cart, created = Cart.objects.get_or_create(user=request.user)
    # get all cart items for this user
    cart_items = CartItem.objects.filter(cart=cart)


    ordered_items = (
            OrderItem.objects
            .filter(order__user=user)
            .select_related("product", "order")
            .prefetch_related("product__productimage_set")  # fetch related images
        )
        # build context dictionary for template
    cart1 = []
    for item in ordered_items:
            # get first image if exists
            product_images = item.product.productimage_set.all()
            image_url = product_images[0].image.url if product_images else ""

            cart1.append({
                "slug":item.product.slug,
                "p_name": item.product.p_name,
                "image_url": image_url,
                "price": float(item.price*item.quantity),  # price at purchase time
                "qty": item.quantity,
                "status": item.order.status,
                "id":item.order.id,
                "date":item.order.created_at

            })
           
    # get only products
    products = []
    for item in cart_items:
        product = item.product
        # dynamically add quantity and subtotal to product object
        product.quantity_in_cart = item.quantity
        product.subtotal_in_cart = item.subtotal()
        products.append(product)
    products = []
    price=0
    log='0'
    if not request.user.is_authenticated:
        log='1'
    else:
        cart, created = Cart.objects.get_or_create(user=request.user)
        products = CartItem.objects.filter(cart=cart).count

        
        
    return render(request, "account.html", {"cart1": cart1,"profile":profile,"is_logged_in": request.user.is_authenticated,
        "user": request.user if request.user.is_authenticated else None,"cart":products,
        "price":price,
        "log":log,})
def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect("login")

    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        # Update User fields
        # Get POST values safely
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        zipcode = request.POST.get("zipcode")
        
        # Update User fields only if provided
        if name:
            user.first_name = name
        
        if email:
            user.email = email
        
        user.save()
        
        # Update Profile fields only if provided
        if mobile:
            profile.mobile = mobile
        
        if address:
            profile.address = address
        
        if zipcode:
            profile.zip_code = zipcode
        
        profile.save()


        from django.contrib import messages
        messages.success(request, "Profile updated successfully!")

        return redirect("myaccount")
    
    return redirect("myaccount")