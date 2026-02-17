from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404
from .models import Cart, CartItem, Product, ProductImage,OfferImage
from datetime import datetime,timedelta

def cart(request):
    products = []
    productsr = []
    price=0
    log='0'
    if not request.user.is_authenticated:
        log='1'
        productcount='0'
    else:
        cart, created = Cart.objects.get_or_create(user=request.user)
        productcount = CartItem.objects.filter(cart=cart).count
        cartproducts=CartItem.objects.filter(cart=cart,carttype="0")
        cart_items = CartItem.objects.filter(cart=cart,carttype="0")
        rentalproducts=CartItem.objects.filter(cart=cart,carttype="1")
        rental_items = CartItem.objects.filter(cart=cart,carttype="1")

        
        for item in cart_items:
            product = item.product
            # attach quantity and subtotal
            price+=item.quantity*product.price
            product.cart_item_id=item.id
            product.quantity_in_cart = item.quantity
            product.subtotal_in_cart = item.subtotal()
            # attach first image url (or None if no image)
            first_image = product.productimage_set.first()
            product.image_url = first_image.image.url if first_image else ""
            products.append(product)
        for item in rental_items:
            productr = item.product
            # attach quantity and subtotal
            
            productr.quantity_in_cart = item.quantity
            productr.cart_item_id=item.id
            productr.subtotal_in_cart = item.subtotal()
            productr.status=item.status
            # attach first image url (or None if no image)
            first_image = productr.productimage_set.first()
            productr.image_url = first_image.image.url if first_image else ""
            productsr.append(productr)
    c={
        "cart":productcount,
        "carts":products,
        "rental":productsr,
        "price":price,
        "log":log,
        "is_logged_in": request.user.is_authenticated,
        "user": request.user if request.user.is_authenticated else None,
    }
    return render(request,"shoppingcart.html",c)


def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        return redirect("login")

    product = get_object_or_404(Product, slug=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    quantity = int(request.POST.get("quantity", 1))

    # Check if product already in cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product,carttype="0")
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    return redirect(request.META.get("HTTP_REFERER", "home"))
def add_to_rental(request, product_id):
    if not request.user.is_authenticated:
        return redirect("login")

    product = get_object_or_404(Product, slug=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    quantity = int(request.POST.get("quantity", 1))

    # Check if product already in cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product,carttype="1")
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    return redirect(request.META.get("HTTP_REFERER", "home"))
from django.shortcuts import get_object_or_404, redirect

def update_cart_quantity(request, cart_item_id,type):
    if not request.user.is_authenticated:
        return redirect("login")

    cart_item = get_object_or_404(
        CartItem,
        id=cart_item_id,
        cart__user=request.user,
        carttype=type
        
    )

    if request.method == "POST":
        action = request.POST.get("action")
        quantity = cart_item.quantity

        if action == "increase":
            cart_item.quantity = quantity + 1
        elif action == "decrease" and quantity > 1:
            cart_item.quantity = quantity - 1

        cart_item.save()

    return redirect("cart")
def remove_from_cart(request, item_id,type):
    if not request.user.is_authenticated:
        return redirect("login")

    cart_item = get_object_or_404(CartItem, product_id=item_id, cart__user=request.user,carttype=type)
    cart_item.delete()  # deletes the item from cart

    return redirect(request.META.get("HTTP_REFERER", "home"))