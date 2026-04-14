from django.shortcuts import render, get_object_or_404
from .models import Product, ProductImage, Cart, CartItem


# ─────────────────────────────────────────────
#  Helper: build product dict from queryset
# ─────────────────────────────────────────────
def get_product_data1(products):
    product_list = []
    for product in products:
        # 1. Try 'first' priority image
        product_image = ProductImage.objects.filter(
            p_id=product, priority='first'
        ).first()

        # 2. Fallback to any image for this product
        if not product_image:
            product_image = ProductImage.objects.filter(p_id=product).first()

        # 3. Safely resolve URL — never let it be None
        if product_image and product_image.image and hasattr(product_image.image, 'url'):
            try:
                image_url = product_image.image.url
            except Exception:
                image_url = None
        else:
            image_url = None

        product_dict = {
            'p_id':           product.p_id,
            'p_name':         product.p_name,
            'point1':         product.point1,
            'point2':         product.point2,
            'brand_name':     product.brand_name,
            'desc':           product.desc,
            'price':          product.price,
            'del_price':      product.del_price,
            'save':           product.save_upto,
            'category':       product.category.c_name,
            'delivery_times': product.delivery_times,
            'new':            product.new,
            'stock_status':   product.stock_status,          # e.g. "in stock" / "out of stock"
            'where':          product.where_in_home,
            'where_to_display': product.where_to_display,
            'slug':           product.slug,
            'image_url':      image_url,                     # ← guaranteed str or None
            'availablity':    str(product.availablity),      # ← coerce to str for template comparison
        }
        product_list.append(product_dict)
    return product_list


# ─────────────────────────────────────────────
#  Product Detail View
# ─────────────────────────────────────────────
def product_detail(request, p):

    # ── Specific product ──────────────────────
    product_obj  = get_object_or_404(Product, slug=p)
    product      = get_product_data1([product_obj])[0]   # dict

    # ── Other images (non-primary) ────────────
    product_other_image = ProductImage.objects.filter(
        p_id=product_obj.p_id, priority='No'
    )

    # ── Same-brand products ───────────────────
    same_brand_products = get_product_data1(
        Product.objects.filter(brand_name=product_obj.brand_name)
                       .exclude(p_id=product_obj.p_id)
    )

    # ── Same-category products ────────────────
    same_category_products = get_product_data1(
        Product.objects.filter(category=product_obj.category)
                       .exclude(p_id=product_obj.p_id)
    )

    # ── Cart count ────────────────────────────
    cart_count = 0
    log        = '1'  # '1' = not logged in

    if request.user.is_authenticated:
        log  = '0'
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = CartItem.objects.filter(cart=cart).count()

    # ── Current canonical URL ─────────────────
    current_url = request.build_absolute_uri()

    context = {
        'product':               product,
        'product_other_image':   product_other_image,
        'same_brand_products':   same_brand_products,
        'same_category_products': same_category_products,
        'cart':                  cart_count,
        'log':                   log,
        'is_logged_in':          request.user.is_authenticated,
        'user':                  request.user if request.user.is_authenticated else None,
        'current_url':           current_url,
    }
    return render(request, 'productdetails-fullwidth.html', context)


def singleproduct(request):
    return render(request, 'productdetails-fullwidth.html')