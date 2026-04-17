import razorpay, random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import Cart, PendingOrder, Product, Order,CartItem, OrderItem, Coupon, UserProfile,UserProfile
from django.shortcuts import redirect
from .models import UserProfile
from django.contrib import messages
from django.shortcuts import redirect
import logging
logger = logging.getLogger(__name__)
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_order_email(user, order):
    items_html = ""
    total = 0

    for item in order.items.all():
        items_html += f"""
        <tr>
            <td>{item.product.p_name}</td>
            <td>{item.quantity}</td>
            <td>₹{item.price}</td>
        </tr>
        """
        total += item.subtotal()

    html_content = f"""
    <html>
    <body style="font-family:Poppins,Arial;background:#f6f6f6;padding:20px;">
        <div style="max-width:600px;margin:auto;background:#fff;border-radius:10px;overflow:hidden;">
            
            <div style="background:#000;color:#fff;padding:20px;text-align:center;">
                <h2>🎉 Order Confirmed</h2>
            </div>

            <div style="padding:20px;">
                <p>Hi <b>{user.username}</b>,</p>
                <p>Your order has been placed successfully ✅</p>

                <h3>Order Details</h3>

                <table width="100%" cellpadding="10" cellspacing="0" style="border-collapse:collapse;">
                    <tr style="background:#000;color:#fff;">
                        <th align="left">Product</th>
                        <th align="left">Qty</th>
                        <th align="left">Price</th>
                    </tr>
                    {items_html}
                </table>

                <p style="margin-top:15px;"><b>Total: ₹{round(total,2)}</b></p>

                <p><b>Payment Method:</b> {order.payment_method.upper()}</p>
                <p><b>Delivery Address:</b> {order.address}</p>

                <br>
                <p>We’ll notify you when your order is shipped 🚚</p>
            </div>

            <div style="background:#f1f1f1;padding:10px;text-align:center;font-size:12px;">
                Tharatrinket • Thank you for shopping with us 💖
            </div>

        </div>
    </body>
    </html>
    """

    email = EmailMultiAlternatives(
        subject="Your Order is Confirmed 🛍️",
        body="Order placed successfully",
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()
def check_userprofile_complete(request):
    
    user = request.user

    if not user.is_authenticated:
        messages.warning(request, "Please log in to continue.")
        return redirect("login")

    try:
        profile, created = UserProfile.objects.get_or_create(user=user)
    except OSError as e:
        # This captures disk/storage-related I/O errors
        logger.exception(f"I/O error while fetching/creating UserProfile for user {user.id}: {e}")
        messages.error(request, "Temporary profile issue. Please try again later.")
        return redirect("myaccount")
    except Exception as e:
        logger.exception(f"Unexpected error in check_userprofile_complete: {e}")
        messages.error(request, "Something went wrong while checking your profile.")
        return redirect("myaccount")

    # ✅ Pull all values safely
    mobile = (getattr(profile, "mobile", "") or "").strip()
    address = (getattr(profile, "address", "") or "").strip()
    zip_code = (getattr(profile, "zip_code", getattr(profile, "zipcode", "")) or "").strip()

    if not mobile or not address or not zip_code:
        messages.warning(request, "Please complete your profile before proceeding.")
        return redirect("/myaccount")

    return None










# ------------------ CHECKOUT PAGE ------------------
@csrf_exempt
@login_required
def cart_checkout(request):
    check = check_userprofile_complete(request)
    if check:  # means function returned a redirect
        return check

    # ✅ All profile fields complete — continue checkout
    ...

    cart = Cart.objects.get(user=request.user)
    items = CartItem.objects.filter(cart=cart,carttype="0")
    if not items.exists():
        return redirect("cart")
    
    total_amount = sum(item.subtotal() for item in items)
    total_paise = int(total_amount * 100)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({
        "amount": total_paise,
        "currency": "INR",
        "payment_capture": "1"
    })

    profile = UserProfile.objects.get(user=request.user)
    log='0'
    if not request.user.is_authenticated:
        log='1'
    if(total_amount<2000):
        total_amount+=100;

    return render(request, "checkout.html", {
        "items": items,
        "total_amount": total_amount,
        "order_id": razorpay_order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "callback_url": "/payment/success-cart/",
        "profile": profile,
        
        "log":log,
    })


# ------------------ SEND OTP ------------------
@csrf_exempt
@login_required
def send_checkout_otp(request):
    if request.method == "POST":
        otp = random.randint(100000, 999999)
        request.session["checkout_otp"] = str(otp)

        send_mail(
            subject="Your Checkout OTP",
            message=f"Your OTP for checkout verification is {otp}. It will expire in 5 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=True,
        )
        return JsonResponse({"status": "sent"})
    return JsonResponse({"status": "error"}, status=400)


# ------------------ VERIFY OTP ------------------

@csrf_exempt
@login_required
def verify_order_otp(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body.decode("utf-8"))
        user_otp = data.get("otp")
        session_otp = request.session.get("checkout_otp")

        if not session_otp:
            return JsonResponse({"status": "no_otp"})

        if str(user_otp) == session_otp:
            del request.session["checkout_otp"]
            request.session["otp_verified"] = True
            return JsonResponse({"status": "verified"})
        return JsonResponse({"status": "invalid"})
    return HttpResponseBadRequest()


# ------------------ APPLY COUPON ------------------
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Cart, Coupon
from datetime import date
import json

@login_required
def apply_coupon(request):
    print("Received coupon apply request:", request.body)

    if request.method == "POST":
        try:
            # Parse JSON data
            data = json.loads(request.body.decode("utf-8"))
            code = (data.get("coupon") or "").strip()

            if not code:
                return JsonResponse({
                    "status": "invalid",
                    "message": "Please enter a coupon code."
                })

            # Get user's cart
            cart = Cart.objects.filter(user=request.user).first()
            if not cart:
                return JsonResponse({
                    "status": "invalid",
                    "message": "Your cart is empty."
                })

            items = CartItem.objects.filter(cart=cart,carttype="0")
            if not items.exists():
                return JsonResponse({
                    "status": "invalid",
                    "message": "Your cart is empty."
                })

            total = sum(item.subtotal() for item in items)

            # ✅ Safely get active coupon
            coupon = Coupon.objects.filter(code__iexact=code, active=True).first()
            if not coupon:
                return JsonResponse({
                    "status": "invalid",
                    "message": "Invalid or inactive coupon."
                })

            # ✅ Check expiry
            if coupon.expiry_date and coupon.expiry_date < date.today():
                return JsonResponse({
                    "status": "invalid",
                    "message": "This coupon has expired."
                })

            # ✅ Calculate discount
            if hasattr(coupon, "discount_percent") and coupon.discount_percent:
                discount = (total * coupon.discount_percent) / 100
            else:
                discount = getattr(coupon, "discount_amount", 0)

            new_total = max(total - discount, 0)
            if(total<2000):
                new_total+=100
            # ✅ Store in session for later use (like order or Razorpay)
            request.session["applied_coupon"] = {
                "code": coupon.code,
                "discount": float(discount),
                "new_total": float(new_total)
            }
            
            # ✅ Return JSON response
            return JsonResponse({
                "status": "ok",
                "total": round(new_total, 2),
                "message": f"Coupon '{coupon.code}' applied successfully! You saved ₹{round(discount,2)}.+if total price is more than 2000 .then not applicable +₹100 for delivery charge"
            })

        except Exception as e:
            print("Error applying coupon:", e)
            return JsonResponse({
                "status": "error",
                "message": "Something went wrong while applying the coupon."
            })

    # If method is not POST
    return JsonResponse({
        "status": "error",
        "message": "Invalid request method."
    })



# ------------------ SAVE ADDRESS (AJAX from Edit) ------------------
@login_required
def edit(request):
    import json
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        address = data.get("address")
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        if address:
            profile.address = address
            profile.save()
            return JsonResponse({"status": "ok"})
        return JsonResponse({"status": "error"})
    return HttpResponseBadRequest()


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import json
from .models import Cart, CartItem, Order, OrderItem, Coupon
@csrf_exempt
@login_required
def place_cod_order(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    # Parse JSON from frontend
    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"status": "error", "message": "Invalid JSON data."})

    # Ensure OTP is verified
    if not request.session.get("otp_verified"):
        return JsonResponse({"status": "error", "message": "OTP not verified."})

    address = data.get("address", "").strip()
    coupon_code = data.get("coupon", "").strip()

    # Fetch user's cart
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Cart not found."})

    cart_items = CartItem.objects.filter(cart=cart,carttype="0")
    item_count = cart_items.count()
    if not cart_items.exists():
        return JsonResponse({"status": "error", "message": "Your cart is empty."})

    # Calculate total amount
    
   
    profile = request.user.userprofile   # ✔ Fetch profile
    
    order = Order.objects.create(
        user=request.user,
        address=profile.address,          # ✔ Correct address
        payment_method='cod',
        status='pending'
    )
    # Create Order Items
    item_count = cart_items.count()
    cart_items = cart.items.all()
    subtotal = sum(item.product.price * item.quantity for item in cart_items)

    if not cart_items.exists():
        return JsonResponse({"status": "error", "message": "Your cart is empty."})

    # 1) Subtotal
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    
    # 2) Discount
    discount_amount = 0
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
            if coupon.is_valid():
                discount_amount = (subtotal * coupon.discount_percent) / 100
        except Coupon.DoesNotExist:
            pass
    
    # 3) Delivery charge (correct formula)
    subtotal_after_discount = subtotal - discount_amount
    delivery_charge = 100 if subtotal_after_discount < 2000 else 0
    i=0
    
    # 4) Split into items
    for item in cart_items:
        item_total = item.product.price * item.quantity
    
        item_share = item_total / subtotal
        item_discount = discount_amount * item_share
        item_delivery = delivery_charge * item_share
    
        final_item_total = item_total - item_discount 
        
        unit_price = final_item_total / item.quantity
        
        
    
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=unit_price
        )
    send_order_email(request.user, order)


    # Clear the cart
    cart_items.delete()
    cart.delete()

    # Remove OTP flag
    request.session.pop("otp_verified", None)

    # Return success response
    return JsonResponse({
        "status": "placed",
        "redirect": reverse("myaccount")  # or "/myaccount"
    })




# ------------------ CREATE RAZORPAY ORDER (AJAX) ------------------
import json
import razorpay
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Sum
from .models import CartItem

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

import json
import razorpay
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Cart, CartItem, Order, OrderItem, Coupon
@csrf_exempt
@login_required
def create_razorpay_order_cart(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    # ✅ OTP verification
    if not request.session.get("otp_verified"):
        return JsonResponse({"status": "error", "message": "OTP not verified."})

    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"status": "error", "message": "Invalid JSON."})

    coupon_code = data.get("coupon", "").strip()
    address = data.get("address", "").strip()

    # ✅ Fetch cart and items
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Cart not found."})

    cart_items = CartItem.objects.filter(cart=cart,carttype="0")
    if not cart_items.exists():
        return JsonResponse({"status": "error", "message": "Cart empty."})

    # ✅ Calculate total
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    # ✅ Apply coupon
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
            if coupon.is_valid():
                discount = (total_amount * coupon.discount_percent) / 100
                total_amount -= discount
        except Coupon.DoesNotExist:
            pass
    if(total_amount<2000):
        total_amount+=100
        

    amount_paise = int((total_amount) * 100)

    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'payment_capture': '1'
        })

        print("✅ Razorpay order created:", razorpay_order)

        # ✅ Store pending order details in session
        request.session["pending_order"] = {
            "razorpay_order_id": razorpay_order["id"],
            "total_amount": float(total_amount),
            "address": address,
        }
        razorpay_order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "payment_capture": "1",
            })
        order_id = razorpay_order["id"]
        request.session[f"order_{order_id}"] = {
        "product_slug": "",
        "quantity":"0",
        "coupon": coupon_code,
        "address": address
    }
        PendingOrder.objects.create(
        order_id=order_id,
        user=request.user,
        product_slug="assdd",
        quantity=0,
        coupon=coupon_code,
        address=address
    )
        # ✅ Respond to frontend JS
        return JsonResponse({
            "status": "created",
            "key": settings.RAZORPAY_KEY_ID,
            "amount": amount_paise,
            "order_id": razorpay_order["id"]
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("❌ Razorpay order creation error:", e)
        return JsonResponse({"status": "error", "message": str(e)})


# ------------------ PAYMENT SUCCESS (RAZORPAY) ------------------
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Cart, Order, OrderItem
@csrf_exempt
def payment_success_cart(request):
    if request.method == "POST":
        
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")

        # fetch pending order details
        pending = PendingOrder.objects.filter(order_id=razorpay_order_id).first()
        coupon_code = pending.coupon

        if pending is None:
            return HttpResponse("Pending order not found", status=400)

        user = pending.user          # ⭐ GET USER FROM DATABASE (NOT request.user)
        profile = user.userprofile  
        # create the final order
        order = Order.objects.create(
            user=user,
            status="paid",
            payment_id=razorpay_payment_id,
            payment_method="online",
            address=profile.address
        )

        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all()  # ⭐ DEFINE FIRST
        item_count = cart_items.count()
        cart_items = cart.items.all()
        subtotal = sum(item.product.price * item.quantity for item in cart_items)

        if not cart_items.exists():
            return JsonResponse({"status": "error", "message": "Your cart is empty."})
    
        # Calculate total amount
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
    
        # Apply coupon if any
        discount_amount = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
                if coupon.is_valid():
                    discount_amount = (subtotal * coupon.discount_percent) / 100
            except Coupon.DoesNotExist:
                pass

        user=request.user
        delivery_charge = 100 if subtotal < 2000 else 0
        for item in cart_items:
                item_total = item.product.price * item.quantity
            
                # proportion of cart
                item_share = item_total / subtotal  
            
                # discount part for this item
                item_discount = discount_amount * item_share  
            
                # delivery charge part
                item_delivery = delivery_charge * item_share
            
                # final total price for this product in the order
                final_item_total = item_total - item_discount 
            
                # per unit price
                unit_price = final_item_total / item.quantity
            
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=unit_price  # save final per-unit price
                )
        send_order_email(request.user, order)
    
        # ✅ Cleanup
        cart_items.delete()
        cart.delete()
        request.session.pop("otp_verified", None)
        request.session.pop("pending_order", None)
    
        return redirect("myaccount")