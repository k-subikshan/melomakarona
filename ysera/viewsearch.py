from django.shortcuts import render
from django.db.models import Case, When, Value, IntegerField, Count
from rapidfuzz import fuzz
import re, unicodedata
from urllib.parse import unquote

from .models import Cart, CartItem, OfferImage, Product
from .viewhome import get_product_data1
from django.core.paginator import Paginator


def search(request, s, page):
    # --- QUERY ---
    if s == "0":
        query = unquote(request.GET.get("q", "")).strip()
    elif s != "100":
        query = unquote(s).strip()
    else:
        query = ""

    sort_by = request.GET.get("SortBy", "manual")
    category_filter = request.GET.get("category")
    stock_filter = request.GET.get("stock")
    size_filter = request.GET.get("size")

    results = []

    # --- NORMALIZE FUNCTION ---
    def normalize(text):
        text = str(text or "").lower()
        text = text.replace("&", "and").replace("–", "-").replace("—", "-").replace("\xa0", " ")
        text = unicodedata.normalize("NFKD", text)
        text = re.sub(r"[^a-z0-9]+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    # --- SEARCH ---
    if query:
        query_norm = normalize(query)
        request.session['search_query'] = query

        strong_results = []

        for p in Product.objects.select_related('category').all():
            name = normalize(p.p_name)
            category = normalize(p.category.c_name)
            desc = normalize(p.desc)

            # --- FUZZY SCORES ---
            name_ratio = fuzz.token_sort_ratio(query_norm, name)
            partial_ratio = fuzz.partial_ratio(query_norm, name)
            token_set = fuzz.token_set_ratio(query_norm, name)

            score = max(name_ratio, partial_ratio, token_set)

            # --- FINAL MATCH CONDITION (FIXED) ---
            if (
                name_ratio >= 80
                or token_set >= 75

                # ✅ 70+ MATCH
                or name_ratio >= 70
                or partial_ratio >= 70

                # ✅ MULTI-WORD MATCH (MAIN FIX)
                or any(word in name for word in query_norm.split())

                # ✅ CATEGORY MATCH
                or any(word in category for word in query_norm.split())

                # ✅ DESCRIPTION MATCH
                or any(word in desc for word in query_norm.split())
            ):
                strong_results.append(p)

        matched_ids = [p.p_id for p in strong_results]

        # --- NO RESULT ---
        if not matched_ids:
            results = []

        else:
            preserve_order = Case(
                *[When(p_id=pid, then=Value(pos)) for pos, pid in enumerate(matched_ids)],
                output_field=IntegerField(),
            )

            filtered_products = (
                Product.objects.filter(p_id__in=matched_ids)
                .annotate(_order=preserve_order)
                .order_by("_order")
            )

            filtered_products.query.clear_ordering(force=True)

            results = get_product_data1(filtered_products)

    else:
        results = []

    # --- FILTERS ---
    filtered_products = Product.objects.filter(p_id__in=[r["p_id"] for r in results])

    if category_filter:
        filtered_products = filtered_products.filter(category__c_name__iexact=category_filter)

    if stock_filter in ["in stock", "out of stock"]:
        filtered_products = filtered_products.filter(stock_status=stock_filter)

    if size_filter:
        filtered_products = filtered_products.filter(size=size_filter)

    # --- SORT ---
    sort_mapping = {
        'manual': None,
        'title-ascending': 'p_name',
        'title-descending': '-p_name',
        'price-ascending': 'price',
        'price-descending': '-price',
        'created-descending': '-p_id',
        'created-ascending': 'p_id',
    }

    if sort_mapping.get(sort_by):
        filtered_products = filtered_products.order_by(sort_mapping[sort_by])

    # FINAL CONVERT
    results = get_product_data1(filtered_products)

    # --- PAGINATION ---
    paginator = Paginator(results, 10)
    page_product = paginator.get_page(page)

    # --- CATEGORY COUNT ---
    category_with_counts = (
        Product.objects.values("category")
        .annotate(total=Count("p_id"))
        .order_by("category")
    )

    # --- CART ---
    if not request.user.is_authenticated:
        cart_count = 0
        log = '1'
    else:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_count = CartItem.objects.filter(cart=cart).count()
        log = '0'

    offers = OfferImage.objects.filter(active=True, where_to_display='6')

    context = {
        'query': query,
        'results': page_product,
        'currentpage': page,
        'page_range': paginator.page_range,
        'ifprev': page_product.has_previous(),
        'ifnext': page_product.has_next(),
        'prevpage': page_product.previous_page_number() if page_product.has_previous() else None,
        'nextpage': page_product.next_page_number() if page_product.has_next() else None,
        'sort_by': sort_by,
        "category_list": category_with_counts,
        "cart": cart_count,
        "log": log,
        "offers": offers,
        "is_logged_in": request.user.is_authenticated,
        "user": request.user if request.user.is_authenticated else None,
        's': s,
    }

    return render(request, 'shop.html', context)