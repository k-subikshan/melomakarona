from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Count, Case, When, Value, IntegerField

from .models import (
    Product,
    Cart,
    CartItem,
    OfferImage
)

from .viewhome import get_product_data1


def searchbycategory(request, s, h, w, d, page):

    query = h

    # =====================================================
    # CATEGORY FILTER
    # =====================================================
    if h=="Others":
        products = Product.objects.filter(   
            category__c_name__iexact=h
        ).distinct()
    elif w=="category":
        products= Product.objects.filter(category__c_name=h)
    
    elif w == "shop_by_type":

        products = Product.objects.filter(
            category__c_name=h,
            shop_by_type__name=d
            
        )

    elif w == "shop_by_occasion":

        products = Product.objects.filter(
            category__c_name=h,
            shop_by_occasion__name=d
        )

    elif w == "shop_by_collection":

        products = Product.objects.filter(
            category__c_name=h,
            shop_by_collection__name=d
        )
    
    else:

        products = Product.objects.filter(
            category__c_name__iexact=h
        ).distinct()

    # =====================================================
    # GET FILTER VALUES
    # =====================================================

    sort_by = request.GET.get(
        "SortBy",
        "manual"
    )

    category_filter = request.GET.get(
        "category"
    )

    brand_filter = request.GET.get(
        "brand"
    )

    stock_filter = request.GET.get(
        "stock"
    )

    size_filter = request.GET.get(
        "size"
    )

    results = []

    same_category_products = []

    same_main_category_diff_products = []

    # =====================================================
    # SEARCH
    # =====================================================

    if query:

        request.session["search_query"] = query

        matched_ids = list(
            products.values_list(
                "p_id",
                flat=True
            )
        )

        if matched_ids:

            preserve_order = Case(

                *[
                    When(
                        p_id=pid,
                        then=Value(pos)
                    )

                    for pos, pid in enumerate(
                        matched_ids
                    )
                ],

                output_field=IntegerField(),
            )

            filtered_products = (

                Product.objects

                .filter(
                    p_id__in=matched_ids
                )

                .annotate(
                    _order=preserve_order
                )

                .order_by("_order")
            )

            results = get_product_data1(
                filtered_products
            )

        else:

            results = []

    else:

        filtered_products = Product.objects.none()

        results = get_product_data1(
            filtered_products
        )

    # =====================================================
    # APPLY FILTERS
    # =====================================================

    filtered_products = Product.objects.filter(
        p_id__in=[r["p_id"] for r in results]
    )

    if category_filter:

        filtered_products = filtered_products.filter(
            category__c_name__iexact=
            category_filter
        )

    if brand_filter:

        filtered_products = filtered_products.filter(
            brand_name__iexact=
            brand_filter
        )

    if stock_filter:

        filtered_products = filtered_products.filter(
            stock_status__iexact=
            stock_filter
        )

    if size_filter:

        filtered_products = filtered_products.filter(
            size__size__iexact=
            size_filter
        )

    # =====================================================
    # SORTING
    # =====================================================

    sort_mapping = {

        'manual': None,

        'best-selling': '-where',

        'title-ascending': 'p_name',

        'title-descending': '-p_name',

        'price-ascending': 'price',

        'price-descending': '-price',

        'created-descending': '-p_id',

        'created-ascending': 'p_id',
    }

    if sort_mapping.get(sort_by):

        filtered_products = filtered_products.order_by(
            sort_mapping[sort_by]
        )

    # =====================================================
    # FINAL RESULTS
    # =====================================================

    results = get_product_data1(
        filtered_products
    )

    # =====================================================
    # COUNTS
    # =====================================================

    category_with_counts = (

        Product.objects

        .values("category")

        .annotate(
            total=Count("p_id")
        )

        .order_by("category")
    )

    stock_counts = (

        Product.objects

        .values("category__c_name")

        .annotate(
            total=Count("p_id")
        )

        .order_by("category__c_name")
    )

    selected_brands = request.GET.getlist(
        "brand"
    )

    selected_sizes = request.GET.getlist(
        "size"
    )

    # =====================================================
    # CART
    # =====================================================

    products_count = 0

    price = 0

    log = "0"

    if not request.user.is_authenticated:

        log = "1"

    else:

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        products_count = CartItem.objects.filter(
            cart=cart
        ).count()

    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        results,
        12
    )

    page_product = paginator.get_page(
        page
    )

    total_page = paginator.page_range

    ifprev = page_product.has_previous()

    ifnext = page_product.has_next()

    prevpage = (

        page_product.previous_page_number()

        if ifprev else None
    )

    nextpage = (

        page_product.next_page_number()

        if ifnext else None
    )

    # =====================================================
    # OFFERS
    # =====================================================

    offers = OfferImage.objects.filter(
        active=True,
        where_to_display='6'
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {

        'query': query,

        'page_range': total_page,

        's': s,
    'h': h,

    'w': w,

    'd': d,

        "offers": offers,

        'ifprev': ifprev,

        "ifnext": ifnext,

        "nextpage": nextpage,

        "prevpage": prevpage,

        'results': page_product,

        'currentpage': page,

        'same_category_products':
            same_category_products,

        'same_main_category_diff_products':
            same_main_category_diff_products,

        'sort_by': sort_by,

        'result': results,

        "category_list":
            category_with_counts,

        "stock_counts":
            stock_counts,

        "selected_size":
            selected_sizes,

        "selected_brands":
            selected_brands,

    

        "cart": products_count,

        "price": price,

        "log": log,

        "is_logged_in":
            request.user.is_authenticated,

        "user":
            request.user
            if request.user.is_authenticated
            else None,
    }

    return render(
        request,
        'shop1.html',
        context
    )


  