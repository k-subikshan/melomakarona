from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Cart

@login_required
def rental_cart_enquiry(request):
    user = request.user

    try:
        cart = Cart.objects.get(user=user)
        rental_items = cart.items.filter(carttype='1')  # ONLY rental items
    except Cart.DoesNotExist:
        return redirect('cart')

    if not rental_items:
        return redirect('cart')

    # Build product list
    product_list = ""
    total_items = 0

    for item in rental_items:
        product_list += f"""
        <tr>
            <td>{item.product.p_name}</td>
            <td>{item.quantity}</td>
            <td>₹{item.product.rentalprice}</td>
        </tr>
        """
        total_items += item.quantity

    subject = f"Rental Enquiry from {user.username}"

    html_content = f"""
    <h2>🛍️ Rental Cart Enquiry</h2>

    <p><strong>Customer Name:</strong> {user.username}</p>
    <p><strong>Email:</strong> {user.email}</p>

    <hr>

    <h3>📦 Requested Rental Products</h3>

    <table border="1" cellpadding="10" cellspacing="0">
        <tr>
            <th>Product</th>
            <th>Quantity</th>
            <th>Rental Price</th>
        </tr>
        {product_list}
    </table>

    <br>
    <p><strong>Total Items:</strong> {total_items}</p>

    <hr>

    <p>Customer is interested in renting these products. Please follow up.</p>

    <p style="color:gray;">Sent from Tharatrinket Website</p>
    """

    email = EmailMultiAlternatives(
        subject,
        "",
        settings.EMAIL_HOST_USER,
        ["tharatrinket@gmail.com"]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

    return redirect('cart')