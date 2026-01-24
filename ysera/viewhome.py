from django.http import HttpResponse
from django.shortcuts import redirect, render,get_object_or_404
from .models import Cart, CartItem, Product, ProductImage,OfferImage,blog
from datetime import datetime,timedelta
# Helper function to get product data including first image
def get_product_data(products):
    product_list = []
    for product in products:
        product_image = ProductImage.objects.filter(p_id=product).first()
        image_url = product_image.image.url if (product_image and product_image.image and hasattr(product_image.image, 'url')) else None
        product_dict = {
            'p_id': product.p_id,
            'p_name': product.p_name,
            
            'brand_name': product.brand_name,
            'desc': product.desc,
            'price': product.price,
            'del_price': product.del_price,
            'category': product.category.c_name,
            'delivery_times': product.delivery_times,
            'save': product.save_upto,                     # new column
            'new': product.new,                       # new column
            'stock_status': product.stock_status,
            'where': product.where_in_home,
            "size":product.size,
            'where_to_display': product.where_to_display,
            'slug': product.slug,
            'image_url': image_url,
            

        }
        product_list.append(product_dict)
    return product_list



def home(request):
    offers_1= OfferImage.objects.filter(active=True,where_to_display='1')
    offers_2= OfferImage.objects.filter(active=True,where_to_display='2')
    offers_3= OfferImage.objects.filter(active=True,where_to_display='3')
    offers_4= OfferImage.objects.filter(active=True,where_to_display='4')
    offers_5= OfferImage.objects.filter(active=True,where_to_display='5')
    # ------------------ FIRST PRODUCTS ------------------
    

    # ------------------ TRENDING PRODUCTS ------------------
    newarrivals_products = Product.objects.filter(where_to_display='home', where_in_home='newarrivals')
    newarrivals_product_data = get_product_data(newarrivals_products)

    # ------------------ BESTSELLING PRODUCTS ------------------
    bestseller_products = Product.objects.filter(where_to_display='home', where_in_home='bestseller')
    bestseller_product_data = get_product_data(bestseller_products)

    # ------------------ LAST PRODUCTS ------------------
    toprated_products = Product.objects.filter(where_to_display='home', where_in_home='toprated')
    toprated_product_data = get_product_data(toprated_products)
    bridalsets_products = Product.objects.filter(where_to_display='home', where_in_home='bridalsets')
    bridalsets_product_data = get_product_data(bridalsets_products)
    products = []
    price=0
    log='0'
    if not request.user.is_authenticated:
        log='1'
    else:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).count
    blogs=blog.objects.all()
        
        
    # ------------------ CONTEXT ------------------
    
    context = {
        
        'newarrivals_products': newarrivals_product_data,
        'bestseller_products': bestseller_product_data,
        'toprated_products': toprated_product_data,
        'bridalsets':bridalsets_product_data,
        "is_logged_in": request.user.is_authenticated,
        "user": request.user if request.user.is_authenticated else None,
        "cart": cart_items,
        "price":price,
        "log":log,
        "offers_1": offers_1,
        "offers_2": offers_2,
        "offers_3": offers_3,
        "offers_4": offers_4,
        "offers_5": offers_5,
        "blog":blogs
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