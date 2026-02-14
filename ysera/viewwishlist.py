from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404
from .models import Cart, CartItem, Product, ProductImage,OfferImage, WishItem, Wishlist
from datetime import datetime,timedelta
from django.core.paginator import Paginator

def wishlist(request,page):
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
        wishlist = Wishlist.objects.filter(user=request.user).first()

        products = []
        seen_product_ids = set()

        if wishlist:
            wish_items = WishItem.objects.filter(wishlist=wishlist).select_related("product")

            for item in wish_items:
                product = item.product

                # skip duplicate products
                if product.p_id in seen_product_ids:
                    continue

                seen_product_ids.add(product.p_id)

                # attach wish item id (first occurrence)
                product.wish_item_id = item.id

                # attach first image
                first_image = product.productimage_set.first()
                product.image_url = first_image.image.url if first_image else ""

                products.append(product)

    page_product1=Paginator(products,6)
    page_product=page_product1.get_page(page)
    total_page=page_product1.page_range
    ifprev=page_product.has_previous()
    ifnext=page_product.has_next()
    prevpage=page_product.previous_page_number
    nextpage=page_product.next_page_number
    c={
           'page_range':total_page,
        "cart":productcount,
        "results":products,
        'ifprev':ifprev,
        "ifnext":ifnext,
        "nextpage":nextpage,
        "prevpage":prevpage,
        "log":log,
        "is_logged_in": request.user.is_authenticated,
        "user": request.user if request.user.is_authenticated else None,
    }
    return render(request,"wishlist.html",c)
def add_to_wishlist(request,product_slug):
    if not request.user.is_authenticated:
        return redirect("login")

    product = get_object_or_404(Product, slug=product_slug)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    wish_item, created = WishItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    return redirect(request.META.get("HTTP_REFERER", "home"))
