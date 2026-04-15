from django.shortcuts import render
from django.db.models import Case, When, Value, IntegerField, Count
from rapidfuzz import fuzz
import re, unicodedata
from .models import Cart, CartItem, OfferImage, Product
from .viewhome import get_product_data1
from django.core.paginator import Paginator


def search(request, s, page):
    # --- DETERMINE QUERY ---
    if s == "0":
        query = request.GET.get("q", "").strip()
    elif s != "100":
        query = s.strip()
    else:
        query = ""

    sort_by = request.GET.get("SortBy", "manual")
    category_filter = request.GET.get("category")
    stock_filter = request.GET.get("stock")
    size_filter = request.GET.get("size")

    results = []

    # --- NORMALIZER ---
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

        def score_product(p):
            name = normalize(p.p_name)
            category = normalize(p.category.c_name)
            combined = f"{name} {category}"

            name_ratio = fuzz.token_sort_ratio(query_norm, name)
            partial_ratio = fuzz.partial_ratio(query_norm, name)
            token_set = fuzz.token_set_ratio(query_norm, name)

            combined_ratio = max(partial_ratio, token_set)

            return max(name_ratio, combined_ratio), name_ratio, token_set

        strong_results = []

        for p in Product.objects.all():
            score, name_ratio, token_set = score_product(p)

            # ✅ SMART + STRICT MATCH
            if (
                name_ratio >= 85
                or token_set >= 80
                or (score >= 80 and len(query_norm) > 3)
            ):
                strong_results.append(p)

        matched_ids = [p.p_id for p in strong_results]

        if matched_ids:
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
            # ✅ STRICT NO RESULTS
            results = []

    else:
        # No query → no results
        results = []

    # --- APPLY FILTERS ---
    filtered_products = Product.objects.filter(p_id__in=[r["p_id"] for r in results])

    if category_filter:
        filtered_products = filtered_products.filter(category__c_name__iexact=category_filter)

    if stock_filter in ["in stock", "out of stock"]:
        filtered_products = filtered_products.filter(stock_status=stock_filter)

    if size_filter:
        filtered_products = filtered_products.filter(size__size=size_filter)

    # --- SORTING ---
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
        filtered_products = filtered_products.order_by(sort_mapping[sort_by])

    # Convert again after filters
    results = get_product_data1(filtered_products)

    # --- PAGINATION ---
    paginator = Paginator(results, 10)
    page_product = paginator.get_page(page)

    # --- EXTRA DATA ---
    category_with_counts = (
        Product.objects.values("category")
        .annotate(total=Count("p_id"))
        .order_by("category")
    )

    stock_counts = (
        Product.objects.values("category__c_name")
        .annotate(total=Count("p_id"))
        .order_by("category__c_name")
    )

    selected_brands = request.GET.getlist("brand")
    selected_sizes = request.GET.getlist("size")

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
        "stock_counts": stock_counts,
        "selected_size": selected_sizes,
        "selected_brands": selected_brands,
        "cart": cart_count,
        "log": log,
        "offers": offers,
        "is_logged_in": request.user.is_authenticated,
        "user": request.user if request.user.is_authenticated else None,
        's': s,
    }

    return render(request, 'shop.html', context)