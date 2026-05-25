from django.shortcuts import render
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page

from .models import (
    Cart, CartItem, Product, ProductImage,
    OfferImage, blog
)


# ---------------- PRODUCT DATA ----------------
def get_product_data(products):
    product_list = []

    for product in products:

        # use prefetched image
        product_image = None

        if hasattr(product, 'prefetched_images'):
            product_image = product.prefetched_images[0] if product.prefetched_images else None

        image_url = (
            product_image.image.url
            if product_image and product_image.image
            else None
        )

        product_dict = {
            'p_id': product.p_id,
            'p_name': product.p_name,
            'brand_name': product.brand_name,
            'desc': product.desc,
            'price': product.price,
            'del_price': product.del_price,
            'category': product.category.c_name,
            'delivery_times': product.delivery_times,
            'save': product.save_upto,
            'new': product.new,
            'stock_status': product.stock_status,
            'where': product.where_in_home,
            'size': product.size,
            'where_to_display': product.where_to_display,
            'slug': product.slug,
            'image_url': image_url,
            'availablity': product.availablity,
        }

        product_list.append(product_dict)

    return product_list


# ---------------- HOME PAGE CACHE ----------------
@cache_page(60 * 15)  # cache for 15 mins
def home(request):

    # ---------------- OFFERS ----------------
    offers_1 = OfferImage.objects.filter(active=True, where_to_display='1')
    offers_2 = OfferImage.objects.filter(active=True, where_to_display='2')
    offers_3 = OfferImage.objects.filter(active=True, where_to_display='3')
    offers_4 = OfferImage.objects.filter(active=True, where_to_display='4')
    offers_5 = OfferImage.objects.filter(active=True, where_to_display='5')

    # ---------------- IMAGE PREFETCH ----------------
    image_prefetch = Prefetch(
        'productimage_set',
        queryset=ProductImage.objects.only('image'),
        to_attr='prefetched_images'
    )

    # ---------------- NEW ARRIVALS ----------------
    newarrivals_products = (
        Product.objects
        .filter(where_to_display='home', where_in_home='newarrivals')
        .select_related('category')
        .prefetch_related(image_prefetch)
    )

    # ---------------- BEST SELLER ----------------
    bestseller_products = (
        Product.objects
        .filter(where_to_display='home', where_in_home='bestseller')
        .select_related('category')
        .prefetch_related(image_prefetch)
    )

    # ---------------- TOP RATED ----------------
    toprated_products = (
        Product.objects
        .filter(where_to_display='home', where_in_home='toprated')
        .select_related('category')
        .prefetch_related(image_prefetch)
    )

    # ---------------- BRIDAL ----------------
    bridalsets_products = (
        Product.objects
        .filter(where_to_display='home', where_in_home='bridalsets')
        .select_related('category')
        .prefetch_related(image_prefetch)
    )

    # ---------------- CONVERT ----------------
    newarrivals_product_data = get_product_data(newarrivals_products)
    bestseller_product_data = get_product_data(bestseller_products)
    toprated_product_data = get_product_data(toprated_products)
    bridalsets_product_data = get_product_data(bridalsets_products)

    # ---------------- LOGIN ----------------
    log = '0'
    price = 0

    if not request.user.is_authenticated:
        log = '1'
        cart_items = 0
    else:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).count()

    # ---------------- BLOGS ----------------
    blogs = blog.objects.all()

    # ---------------- CONTEXT ----------------
    context = {
        'newarrivals_products': newarrivals_product_data,
        'bestseller_products': bestseller_product_data,
        'toprated_products': toprated_product_data,
        'bridalsets': bridalsets_product_data,

        "is_logged_in": request.user.is_authenticated,
        "user": request.user if request.user.is_authenticated else None,

        "cart": cart_items,
        "price": price,
        "log": log,

        "offers_1": offers_1,
        "offers_2": offers_2,
        "offers_3": offers_3,
        "offers_4": offers_4,
        "offers_5": offers_5,

        "blog": blogs
    }

    return render(request, 'index.html', context)
def get_product_data1(products):
    product_list = []
    for product in products:
        product_image = ProductImage.objects.filter(p_id=product).first()
        image_url = product_image.image.url if (product_image and product_image.image and hasattr(product_image.image, 'url')) else None
        sizes = ""

        product_dict = {
            'p_id': product.p_id,
            'p_name': product.p_name,
            'brand_name': product.brand_name,
            'desc': product.desc,
            'price': product.price,
            'del_price': product.del_price,
            'category': product.category.c_name,
            'delivery_times': product.delivery_times,
            'save': product.save_upto,   # make sure field name matches your model
            'new': product.new,
            'size':product.size,
            'stock_status': product.stock_status,
            'where': product.where_in_home,
            'where_to_display': product.where_to_display,
            'slug': product.slug,
            'image_url':image_url
            
        }
        product_list.append(product_dict)
    return product_list