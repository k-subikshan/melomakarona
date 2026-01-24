from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404
from .models import Cart, CartItem, Product, ProductImage,OfferImage
from datetime import datetime,timedelta

def cart(request):
    products = []
    price=0
    log='0'
    if not request.user.is_authenticated:
        log='1'
    else:
        cart, created = Cart.objects.get_or_create(user=request.user)
        productcount = CartItem.objects.filter(cart=cart).count
        cartproducts=CartItem.objects.filter(cart=cart)
        cart_items = CartItem.objects.filter(cart=cart)

        
        for item in cart_items:
            product = item.product
            # attach quantity and subtotal
            price+=item.quantity*product.price
            product.quantity_in_cart = item.quantity
            product.subtotal_in_cart = item.subtotal()
            # attach first image url (or None if no image)
            first_image = product.productimage_set.first()
            product.image_url = first_image.image.url if first_image else ""
            products.append(product)
    c={
        "carts":productcount,
        "cart":products,
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
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()

    return redirect("cart")