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
            <td>₹{item.product.price}</td>
        </tr>
        """
        total_items += item.quantity

    subject = f"Rental Enquiry from {user.username}"

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    body {{
        font-family: 'Poppins', Arial, sans-serif;
        background-color: #f6f6f6;
        padding: 20px;
    }}
    .container {{
        max-width: 600px;
        margin: auto;
        background: #ffffff;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }}
    .header {{
        background: linear-gradient(135deg, #000000, #333333);
        color: white;
        padding: 20px;
        text-align: center;
    }}
    .header h2 {{
        margin: 0;
        letter-spacing: 1px;
    }}
    .content {{
        padding: 20px;
    }}
    .info {{
        margin-bottom: 20px;
    }}
    .info p {{
        margin: 5px 0;
        font-size: 14px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }}
    th {{
        background: #000;
        color: #fff;
        padding: 10px;
        text-align: left;
        font-size: 14px;
    }}
    td {{
        padding: 10px;
        border-bottom: 1px solid #ddd;
        font-size: 14px;
    }}
    tr:nth-child(even) {{
        background: #f9f9f9;
    }}
    .total {{
        margin-top: 15px;
        font-weight: bold;
        font-size: 15px;
    }}
    .footer {{
        background: #f1f1f1;
        padding: 15px;
        text-align: center;
        font-size: 12px;
        color: #777;
    }}
</style>
</head>

<body>

<div class="container">

    <div class="header">
        <h2>🛍️ Rental Enquiry</h2>
    </div>

    <div class="content">

        <div class="info">
            <p><strong>Customer Name:</strong> {user.username}</p>
            <p><strong>Email:</strong> {user.email}</p>
        </div>

        <h3>Requested Products</h3>

        <table>
            <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Price</th>
            </tr>
            {product_list}
        </table>

        <p class="total">Total Items: {total_items}</p>

    </div>

    <div class="footer">
        Sent from Tharatrinket Website • Rental Enquiry System
    </div>

</div>

</body>
</html>
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