from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
# Create your models here.
from django.utils import timezone
import random
class Category(models.Model):
    c_id = models.AutoField(primary_key=True)
    c_name = models.CharField(max_length=100, default="")
    slug = models.SlugField(unique=True, blank=True, null=True, default="")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.c_name) + f"-{self.c_id or '0'}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.c_name
class Product(models.Model):
    p_id = models.AutoField(primary_key=True)
    p_name = models.CharField(max_length=1000, default="")
    point1 = models.CharField(max_length=1000, default="")
    point2= models.CharField(max_length=1000, default="")
    brand_name = models.CharField(max_length=1000, default="")
    desc = models.TextField(default="")
    size= models.CharField(max_length=1000, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    del_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    rentalprice=models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    CHOICES = [
        ('0', 'buy'),
        ('1', 'rental'),
        ('2','both')
        
    ]
    availablity=models.CharField(

        max_length=10,
        choices=CHOICES,
        default='2'
    )

    save_upto=models.IntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)

    delivery_times=models.IntegerField(default=1)

    new_choice=[
        ("yes","yes"),
        ("no","no")
    ]
    new=models.CharField(
    max_length=150,
    choices=new_choice,
    default='yes')
    STOCK_CHOICES = [
    ('in stock', 'In Stock'),
    ('out of stock', 'Out of Stock'),
]

    stock_status = models.CharField(
    max_length=150,
    choices=STOCK_CHOICES,
    default='in stock'
)
    WHERE = [
        ('bestseller','best seller'),
    ('newarrivals', 'new arrivals'),
    ('toprated','top rated'),
    ('bridalsets','Bridal Sets')
    ]
    where_in_home= models.CharField(
        max_length=100,
        choices=WHERE,
        default='none'
    )

    WHERE_TO_DISPLAY_CHOICES = [
        ('none', 'None'),
        ('home', 'Home'),
        
    ]
    where_to_display = models.CharField(
        max_length=10,
        choices=WHERE_TO_DISPLAY_CHOICES,
        default='none'
    )
    slug = models.SlugField(unique=True, blank=True, null=True, default="")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.desc[:50]) + f"-{self.p_id or '0'}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.p_name
# ---------------- PRODUCT IMAGE ----------------
class ProductImage(models.Model):
    img_id = models.AutoField(primary_key=True)
    p_id = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='images', blank=True, null=True, default="")
    CHOICES = [
        ('first', 'first'),
        ('No', 'No'),
        
    ]
    priority= models.CharField(
        max_length=10,
        choices=CHOICES,
        default='none'
    )
    slug = models.SlugField( blank=True, null=True, default="")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"img-{self.img_id or '0'}-{slugify(self.p_id.desc[:20])}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.p_id}"
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    CHOICES = [
        ('0', 'buy'),
        ('1', 'rental'),
        
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    carttype=models.CharField(
        max_length=10,
        choices=CHOICES,
        default='0'
    )

    def __str__(self):
        return f"{self.quantity} x {self.product.p_name}"

    def subtotal(self):
        return self.quantity * self.product.price
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100,default="angels")
    last_name = models.CharField(max_length=100,default="angels")
    address = models.TextField(blank=True, null=True)
    mobile = models.CharField(max_length=15)
    zip_code = models.CharField(max_length=10, null=True, blank=True) 
    def __str__(self):
        return self.user.username
# ---------------- ORDER ----------------
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ]
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online Payment'),
        ('cod', 'Cash on Delivery'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    address = models.TextField(blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)  # Razorpay payment ID
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cod')
    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())
    def __str__(self):
        return f"Order #{self.id} by {self.user.username} ({self.payment_method})"



# ---------------- ORDER ITEM ----------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at purchase time

    def __str__(self):
        return f"{self.quantity} x {self.product.p_name} (Order #{self.order.id})"

    def subtotal(self):
        return ((self.quantity or 0) * (self.price or 0)+100)
from django.utils import timezone
import random

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    def is_valid(self):
        return (timezone.now() - self.created_at).seconds < 300  # 5 mins validity

    def __str__(self):
        return f"OTP for {self.user.username}"
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        return self.active and (not self.expiry_date or self.expiry_date > timezone.now())

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"
class OfferImage(models.Model):
    img_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to="offers", blank=True, null=True)
    Type_CHOICES = [
        ('price', 'price'),
        ('promo code', 'promo code'),    
    ]
    Type = models.CharField(
        max_length=10,
        choices=Type_CHOICES,
        default='none'
    )
    title = models.CharField(max_length=200, blank=True, null=True, default="")
    descripton = models.CharField(max_length=200, blank=True, null=True, default="")
    offers= models.CharField(max_length=200, blank=True, null=True, default="")
    active = models.BooleanField(default=True)
    WHERE_TO_DISPLAY_CHOICES = [
        ('1', 'home-1'),
        ('2', 'home-2'),
        ('3', 'home-3'),
        ('4', 'home-4'),
        ('5', 'home-5'),
        ('6','search')
        
    ]
    where_to_display = models.CharField(
        max_length=10,
        choices=WHERE_TO_DISPLAY_CHOICES,
        default='none'
    )
    offer_applies_to= models.CharField(max_length=200, blank=True, null=True, default="")
    slug = models.SlugField(unique=True, blank=True, null=True, default="")
    

    def save(self, *args, **kwargs):
        # Automatically generate slug if not provided
        if not self.slug:
            base_title = self.title or "offer"
            self.slug = f"offer-{slugify(base_title)}-{self.img_id or '0'}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or f"Offer Image #{self.img_id}"
class blog(models.Model):
    blog_id=models.IntegerField(primary_key=True)
    title=models.CharField(max_length=500)
    image = models.ImageField(upload_to="offers/blog", blank=True, null=True)
    link=models.CharField(max_length=500)
    desc=models.CharField(max_length=500)
    author=models.CharField(max_length=100)
    date=models.DateField( auto_now=False, auto_now_add=False)
class PendingOrder(models.Model):
    order_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product_slug = models.CharField(max_length=200)
    quantity = models.IntegerField(default=1)
    coupon = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wish")
    created_at = models.DateTimeField(auto_now_add=True)
# ---------------- ORDER ITEM ----------------
class WishItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)