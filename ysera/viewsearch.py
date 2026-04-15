from django.shortcuts import render
from django.db.models import Count
from rapidfuzz import fuzz
import re, unicodedata
from django.core.paginator import Paginator

from .models import Cart, CartItem, OfferImage, Product, Category
from .viewhome import get_product_data1


def search(request, s, page):

    # ---------------- QUERY ----------------
    if s == "0":
        query = request.GET.get("q", "").strip()
    elif s != "100":
        query = s.strip()
    else:
        query = ""

    request.session['search_query'] = query

    sort_by = request.GET.get("SortBy", "manual")
    category_filter = request.GET.get("category")
    brand_filter = request.GET.get("brand")
    stock_filter = request.GET.get("stock")
    size_filter = request.GET.get("size")

    # ---------------- NORMALIZER ----------------
    def normalize(text):
        text = str(text or "").lower()
        text = unicodedata.normalize("NFKD", text)
        text = re.sub(r"[^a-z0-9]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    # ---------------- SCORING ----------------
    def score_block(qwords, text):
        t = normalize(text)
        score = 0

        for w in qwords:
            if re.search(rf"\b{re.escape(w)}\b", t):
                score += 400
            elif w in t:
                score += 150

            score += fuzz.partial_ratio(w, t) * 0.5

        if all(w in t for w in qwords):
            score += 300

        return score

    # ---------------- SEARCH LOGIC ----------------
    if query:
        query_norm = normalize(query)
        qwords = query_norm.split()

        scored = []

        for p in Product.objects.all():
            text = f"{p.p_name} {p.brand_name} {p.category.c_name}"

            score = score_block(qwords, text)

            # 🔥 BOOSTS
            if normalize(p.p_name) == query_norm:
                score += 1500
            if normalize(p.brand_name) == query_norm:
                score += 1200
            if normalize(p.category.c_name) == query_norm:
                score += 1000

            scored.append((score, p))

        scored.sort(reverse=True, key=lambda x: x[0])
        ranked_products = [p for score, p in scored]

        # fallback
        if not ranked_products or scored[0][0] < 100:
            ranked_products = list(Product.objects.all())[:20]

    else:
        ranked_products = list(Product.objects.all())

    # ---------------- APPLY FILTERS ----------------
    filtered_products = Product.objects.filter(p_id__in=[p.p_id for p in ranked_products])

    if category_filter:
        filtered_products = filtered_products.filter(category__c_name__iexact=category_filter)

    if brand_filter:
        filtered_products = filtered_products.filter(brand_name__iexact=brand_filter)

    if stock_filter:
        filtered_products = filtered_products.filter(stock_status__iexact=stock_filter)

    if size_filter:
        filtered_products = filtered_products.filter(size__size=size_filter)

    # ---------------- SPECIAL SEARCH (s=100) ----------------
    if '100' in s:
        u = s.split(" ")

        if len(u) >= 3:
            if u[1] == "size":
                size_val = u[2]
                filtered_products = [
                    p for p in Product.objects.all()
                    if size_val in [s.size for s in p.size_set.all()]
                ]
            else:
                filtered_products = filtered_products.filter(brand_name__iexact=u[2])

    # ---------------- SORTING ----------------
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

    # ---------------- CONVERT ----------------
    results = get_product_data1(filtered_products)

    # ---------------- PAGINATION ----------------
    paginator = Paginator(results, 20)
    page_obj = paginator.get_page(page)

    # ---------------- FILTER COUNTS ----------------
    category_with_counts = (
        Product.objects.values("category")
        .annotate(total=Count("p_id"))
        .order_by("category")
    )

    brands_with_counts = (
        Product.objects.values("brand_name")
        .annotate(total=Count("p_id"))
        .order_by("brand_name")
    )

    stock_counts = (
        Product.objects.values("stock_status")
        .annotate(total=Count("p_id"))
        .order_by("stock_status")
    )

    selected_brands = request.GET.getlist("brand")
    selected_sizes = request.GET.getlist("size")

    # ---------------- CART ----------------
    cart_products = []
    price = 0
    log = "0"

    if not request.user.is_authenticated:
        log = "1"
    else:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        for item in CartItem.objects.filter(cart=cart):
            prod = item.product
            price += item.quantity * prod.price
            cart_products.append(prod)

    # ---------------- OFFERS ----------------
    offers = OfferImage.objects.filter(active=True, where_to_display='6')

    # ---------------- FINAL CONTEXT ----------------
    context = {
        'query': query,
        'results': page_obj,
        'page_range': paginator.page_range,
        'currentpage': page,
        'sort_by': sort_by,
        'category_list': category_with_counts,
        'brand_list': brands_with_counts,
        'stock_counts': stock_counts,
        'selected_brands': selected_brands,
        'selected_size': selected_sizes,
        'cart': cart_products,
        'price': price,
        'log': log,
        'offers': offers,
        'is_logged_in': request.user.is_authenticated,
        'user': request.user if request.user.is_authenticated else None,
    }

    return render(request, 'shop.html', context)