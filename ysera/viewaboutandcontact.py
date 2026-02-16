from django.shortcuts import render

from ysera.models import Cart, CartItem
def about(request):
    log='0'
    if not request.user.is_authenticated:
        log='1'
        cart_items="0"
    else:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).count
    c={"is_logged_in": request.user.is_authenticated,
        "user": request.user if request.user.is_authenticated else None,
        "cart": cart_items,
        
        "log":log,}
    return render(request, 'about.html',c  )
def contact(request):
    log='0'
    if not request.user.is_authenticated:
        log='1'
        cart_items="0"
    else:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).count
    c={"is_logged_in": request.user.is_authenticated,
        "user": request.user if request.user.is_authenticated else None,
        "cart": cart_items,
        
        "log":log,}
    return render(request, 'contact.html',c)