from django.contrib import admin
from django.utils.html import mark_safe
from django.db.models import Sum
from django.http import JsonResponse
from django.urls import path
from django.contrib.admin import site
from django.utils.timezone import now
from datetime import timedelta
from django.http import JsonResponse
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from django.utils.timezone import now
from datetime import timedelta
from django.urls import path
from django.contrib.admin import site


from .models import (
    Category, Product, ProductImage,
    Cart, CartItem,
    Order, OrderItem,
    UserProfile, Coupon, OfferImage,blog
)

# ================= ADMIN BRANDING =================
admin.site.site_header = "Zapwaves Jewellery Administration"
admin.site.site_title = "Zapwaves Admin Portal"
admin.site.index_title = "Luxury Jewellery Dashboard"

# ================= CATEGORY =================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("c_id", "c_name", "slug")
    search_fields = ("c_name",)
    prepopulated_fields = {"slug": ("c_name",)}

# ================= PRODUCT IMAGE INLINE =================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    can_delete = True
    fields = ("image", "priority", "image_preview", "DELETE")  # ✅ ADD THIS
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width='70' style='border-radius:10px;'>")
        return "-"

# ================= PRODUCT =================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "p_id",
        "p_name",
        "category",
        "price",
        "rentalprice",
        "availablity",
        "stock_status",
        "where_to_display",

    )
    list_filter = ("category", "stock_status", "where_to_display", "new")
    search_fields = ("p_name", "brand_name", "desc")
    prepopulated_fields = {"slug": ("p_name",)}
    autocomplete_fields = ("category",)
    inlines = [ProductImageInline]
    readonly_fields = ("image_preview",)

    fieldsets = (
        ("💎 Basic Details", {
            "fields": ("p_name", "brand_name", "category", "desc", "slug"),
        }),
        ("✨ Pricing", {
            "fields": ("price", "rentalprice","del_price","availablity", "save_upto"),
        }),
        ("📦 Inventory", {
            "fields": ("stock_status", "size", "delivery_times"),
        }),
        ("🏷 Display Settings", {
            "fields": ("new", "where_in_home", "where_to_display"),
        }),
        ("🖼 Preview", {
            "fields": ("image_preview",),
        }),
    )

    def image_preview(self, obj):
        img = obj.productimage_set.first()
        if img and img.image:
            return mark_safe(
                f"<img src='{img.image.url}' width='90' "
                f"style='border-radius:12px; box-shadow:0 8px 20px rgba(0,0,0,0.4);'>"
            )
        return "No Image"

    image_preview.short_description = "Preview"

# ================= CART =================
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "total_price")

# ================= CART ITEM =================
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "quantity", "subtotal","carttype")
    list_filter=("id", "cart", "product", "quantity","carttype")
    search_fields =("id", "cart", "product", "quantity","carttype")
@admin.register(blog)
class blogAdmin(admin.ModelAdmin):
    list_display = ("blog_id","image","desc","author","date")
    list_filter=("blog_id","image","desc","author","date")
    search_fields =("blog_id","image","desc","author","date")
# ================= USER PROFILE =================
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "mobile", "zip_code")
    search_fields = ("user__username", "mobile")

@admin.action(description="Mark selected orders as Shipped")
def mark_as_shipped(modeladmin, request, queryset):
    queryset.update(status='shipped')

@admin.action(description="Mark selected orders as Delivered")
def mark_as_delivered(modeladmin, request, queryset):
    queryset.update(status='delivered')

from django.contrib import admin
from .models import Order, OrderItem, UserProfile

# Inline admin for OrderItem
class OrderItemInline(admin.TabularInline):  # use admin.StackedInline if you want bigger form
    model = OrderItem
    extra = 0  # show only existing items by default
    fields = ('product', 'quantity', 'price', 'subtotal')
    readonly_fields = ('subtotal',)
from django.contrib import admin
from .models import Order, OrderItem, UserProfile


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_customer_name',
        'get_customer_email',
        'get_customer_mobile',
        'get_user_zipcode',
        'get_ordered_items',
        'total_price',
        'address',
        'payment_method',
        'status',
        'created_at',
    )
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__userprofile__mobile',
        'id',
        'payment_method',
    )
    list_filter = ('status', 'created_at', 'payment_method')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    actions = ['mark_as_shipped', 'mark_as_delivered']

    # ✅ CUSTOMER NAME
    @admin.display(description="Customer Name")
    def get_customer_name(self, obj):
        return obj.user.first_name or obj.user.username or "-"

    # ✅ EMAIL
    @admin.display(description="Email")
    def get_customer_email(self, obj):
        return obj.user.email or "-"

    # ✅ MOBILE NUMBER
    @admin.display(description="Mobile No.")
    def get_customer_mobile(self, obj):
        try:
            return obj.user.userprofile.mobile or "-"
        except UserProfile.DoesNotExist:
            return "-"

    # ✅ ZIPCODE
    @admin.display(description="Zipcode")
    def get_user_zipcode(self, obj):
        try:
            return obj.user.userprofile.zip_code or "-"
        except UserProfile.DoesNotExist:
            return "-"

    # ✅ ORDERED ITEMS
    @admin.display(description="Ordered Items")
    def get_ordered_items(self, obj):
        return ", ".join([
            f"{item.product.p_name} ({item.quantity})"
            for item in obj.items.all()
        ]) or "-"

    # ✅ ACTIONS
    @admin.action(description="Mark selected orders as Shipped")
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')

    @admin.action(description="Mark selected orders as Delivered")
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')

# ================= COUPON =================
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "active", "expiry_date", "is_valid_display")

    def is_valid_display(self, obj):
        return obj.is_valid()

    is_valid_display.boolean = True
    is_valid_display.short_description = "Valid?"

# ================= OFFER IMAGE =================
@admin.register(OfferImage)
class OfferImageAdmin(admin.ModelAdmin):
    list_display = ("img_id", "title", "Type", "active", "where_to_display")
    list_filter = ("active", "Type")
from django.contrib import admin
from .models import Wishlist, WishItem


# ================= WISHLIST =================
@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    list_filter = ("user", "created_at")
    search_fields = ("user__username", "user__email")


# ================= WISHLIST ITEM =================
@admin.register(WishItem)
class WishItemAdmin(admin.ModelAdmin):
    list_display = ("id", "wishlist", "product")
    list_filter = ("wishlist", "product")
    search_fields = ("wishlist__user__username", "product__name")

# ==================================================
# 📊 SALES CHART (MATCHES YOUR MODELS)
# ==================================================

# ======== ANALYTICS FOR PRODUCT & CATEGORY ========

from django.http import JsonResponse
from django.db.models import Sum, F
from django.contrib.admin import site
from django.urls import path

# CATEGORY-WISE SALES
def category_sales_data(request):
    qs = (
        OrderItem.objects
        .filter(order__status="delivered")
        .values(category=F("product__category__c_name"))
        .annotate(revenue=Sum(F("price") * F("quantity")))
        .order_by("-revenue")
    )

    return JsonResponse({
        "labels": [i["category"] for i in qs],
        "values": [float(i["revenue"] or 0) for i in qs],
    })


# PRODUCT-WISE SALES
def product_sales_data(request):
    qs = (
        OrderItem.objects
        .filter(order__status="delivered")
        .values(product_name=F("product__p_name"))
        .annotate(revenue=Sum(F("price") * F("quantity")))
        .order_by("-revenue")[:10]
    )

    return JsonResponse({
        "labels": [i["product"] for i in qs],
        "values": [float(i["revenue"] or 0) for i in qs],
    })


# REGISTER ADMIN URLS (VERY IMPORTANT)
def get_admin_urls(urls):
    def wrapper():
        return [
            path("analytics/category-sales/", site.admin_view(category_sales_data)),
            path("analytics/product-sales/", site.admin_view(product_sales_data)),
        ] + urls
    return wrapper

site.get_urls = get_admin_urls(site.get_urls())

def dashboard_kpi_data(request):
    start = now() - timedelta(days=30)

    revenue = (
        OrderItem.objects
        .filter(order__status="delivered")
        .aggregate(total=Sum(F("price") * F("quantity")))["total"] or 0
    )

    orders = Order.objects.filter(status="delivered").count()
    products = Product.objects.count()
    categories = Category.objects.count()

    daily = (
        OrderItem.objects
        .filter(order__status="delivered", order__created_at__gte=start)
        .annotate(day=TruncDate("order__created_at"))
        .values("day")
        .annotate(total=Sum(F("price") * F("quantity")))
        .order_by("day")
    )

    return JsonResponse({
        "kpi": {
            "revenue": float(revenue),
            "orders": orders,
            "products": products,
            "categories": categories,
        },
        "daily": {
            "labels": [str(i["day"]) for i in daily],
            "values": [float(i["total"]) for i in daily],
        }
    })
def category_sales_data(request):
    qs = (
        OrderItem.objects
        .filter(order__status="delivered")
        .values(category=F("product__category__c_name"))
        .annotate(total=Sum(F("price") * F("quantity")))
        .order_by("-total")
    )
    return JsonResponse({
        "labels": [i["category"] for i in qs],
        "values": [float(i["total"]) for i in qs],
    })


def product_sales_data(request):
    qs = (
        OrderItem.objects
        .filter(order__status="delivered")
        .values(product_name=F("product__p_name"))
        .annotate(total=Sum(F("price") * F("quantity")))
        .order_by("-total")[:8]
    )
    return JsonResponse({
        "labels": [i["product_name"] for i in qs],
        "values": [float(i["total"]) for i in qs],
    })
def get_admin_urls(urls):
    def wrapper():
        return [
            path("analytics/dashboard/", site.admin_view(dashboard_kpi_data)),
            path("analytics/category-sales/", site.admin_view(category_sales_data)),
            path("analytics/product-sales/", site.admin_view(product_sales_data)),
        ] + urls
    return wrapper

site.get_urls = get_admin_urls(site.get_urls())
DATA_UPLOAD_MAX_MEMORY_SIZE = 16777216   # 16 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 16777216   # 16 MB
