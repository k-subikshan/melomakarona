from django.shortcuts import render
from django.db.models import (
    Q,
    Case,
    When,
    Value,
    IntegerField,
    Count
)

from rapidfuzz import fuzz
from django.core.paginator import Paginator

import re
import unicodedata

from .models import (
    Cart,
    CartItem,
    OfferImage,
    Product,
    Category,
    UserProfile
)

from .viewhome import get_product_data1


def search(request, s, page):

    # =====================================================
    # QUERY
    # =====================================================

    # =====================================================
    # QUERY
    # =====================================================

    query = request.GET.get(
        "q",
        ""
    ).strip()

    # fallback from URL
    if not query and s not in ["0", "100"]:

        query = s.strip()

    sort_by = request.GET.get("SortBy", "manual")

    category_filter = request.GET.get("category")

    brand_filter = request.GET.get("brand")

    stock_filter = request.GET.get("stock")

    size_filter = request.GET.get("size")

    results = []

    same_category_products = []

    same_main_category_diff_products = []

    # =====================================================
    # NORMALIZE
    # =====================================================

    def normalize(text):

        text = str(text or "").lower()

        replacements = {

            "maatal": "maattal",
            "matal": "maattal",
            "mattal": "maattal",

            "&": "and",
        }

        for old, new in replacements.items():

            text = text.replace(old, new)

        text = unicodedata.normalize(
            "NFKD",
            text
        )

        text = re.sub(
            r"[^a-z0-9\s]+",
            "",
            text
        )

        text = re.sub(
            r"\s+",
            " ",
            text
        ).strip()

        return text

    # =====================================================
    # SEARCH
    # =====================================================
# =====================================================
# SEARCH
# =====================================================
    if query == "others":
        products = Product.objects.exclude(
            Q(p_name__icontains="bangels") |
            Q(p_name__icontains="bracelets")
        )
    elif query:

        query_norm = normalize(query)

        request.session["search_query"] = query

        query_words = query.lower().split()

        # =================================================
        # DATABASE FILTER
        # =================================================

        db_query = Q()

        for word in query_words:

            db_query |= Q(
                p_name__icontains=word
            )

        products = Product.objects.filter(
            db_query
        ).distinct()

        ranked_products = []

        # =================================================
        # RANK PRODUCTS
        # =================================================

        for product in products:

            original_name = product.p_name.lower()

            normalized_name = normalize(
                product.p_name
            )

            score = 0

            # =============================================
            # 1. PERFECT EXACT MATCH
            # =============================================

            if query.lower() == original_name:

                score += 1000

            # =============================================
            # 2. NORMALIZED EXACT MATCH
            # =============================================

            elif query_norm == normalized_name:

                score += 950

            # =============================================
            # 3. STARTS WITH
            # =============================================

            elif original_name.startswith(
                query.lower()
            ):

                score += 900

            # =============================================
            # 4. QUERY INSIDE PRODUCT NAME
            # =============================================

            elif query.lower() in original_name:

                score += 800

            # =============================================
            # 5. WORD MATCHING
            # =============================================

            matched_words = 0

            for word in query_words:

                if word in original_name:

                    matched_words += 1

            score += matched_words * 100

            # =============================================
            # 6. FUZZY MATCH
            # =============================================

            fuzzy_score = fuzz.token_set_ratio(
                query.lower(),
                original_name
            )

            # =================================================
            # STRICTER FUZZY FOR SINGLE WORDS
            # =================================================

            if len(query_words) == 1:

                score += fuzzy_score * 0.2

            else:

                score += fuzzy_score * 0.5

            # =============================================
            # MINIMUM THRESHOLD
            # =============================================

            if score >= 600:

                ranked_products.append(
                    (product, score)
                )

        # =================================================
        # SORT RESULTS
        # =================================================

        ranked_products.sort(
            key=lambda x: x[1],
            reverse=True
        )

        matched_ids = [
            p[0].p_id
            for p in ranked_products
        ]

        # =================================================
        # KEEP ORDER
        # =================================================

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

        filtered_products = []

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

    products = []

    price = 0

    log = "0"

    if not request.user.is_authenticated:

        log = "1"

    else:

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        products = CartItem.objects.filter(
            cart=cart
        ).count()

    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(results, 12)

    page_product = paginator.get_page(page)

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
        'result':results,

        "category_list":
            category_with_counts,

        "stock_counts":
            stock_counts,

        "selected_size":
            selected_sizes,

        "selected_brands":
            selected_brands,

        'h': filtered_products,

        "cart": products,

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
        'shop.html',
        context
    )