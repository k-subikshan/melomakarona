from django.urls import path
from . import viewhome,viewsingleproduct,viewsearch,viewlogin,viewcart,viewaccount,viewblog,viewcheckout,viewwishlist,viewforgotpass


urlpatterns = [
    path("",viewhome.home,name="home"),
    path("product/<slug:p>",viewsingleproduct.product_detail,name="product"),
    path('<str:s>/pageno<int:page>/search', viewsearch.search, name='search'),
    path('login',viewlogin.login_view,name="login"),
     path("logout/", viewlogin.logout_view, name="logout"),
     path('signup/', viewlogin.signup_view, name='signup'),
     path("cart",viewcart.cart,name="cart"),
     path('cart/add/<slug:product_id>/', viewcart.add_to_cart, name='add to cart'),
     path('rental/add/<slug:product_id>/', viewcart.add_to_rental, name='add to rental'),
        path('myaccount',viewaccount.account_detail,name="myaccount"),
        path('edit',viewaccount.edit_profile,name="edit"),
        path("blog/pageno<int:page>",viewblog.blog1,name="blog"),
        path('cart/update/<int:cart_item_id>/', viewcart.update_cart_quantity, name='add_to_cart'),
path('checkout/cart/', viewcheckout.cart_checkout, name='cart_checkout'),

    path('place-cod-order-cart/', viewcheckout.place_cod_order, name='place_cod_order1'),
   
path('apply-coupon/', viewcheckout.apply_coupon, name='apply_coupon'),
    
path('create-razorpay-order-cart/', viewcheckout.create_razorpay_order_cart, name='create_razorpay_order1'),
path("send-checkout-otp-cart/", viewcheckout.send_checkout_otp, name="send_checkout_otp1"),
path('verify-order-otp-cart/', viewcheckout.verify_order_otp, name='verify_order_otp1'),

    path('payment/success-cart1/', viewcheckout.payment_success_cart, name='payment_success1'),
    path('wishlist/pageno<int:page>',viewwishlist.wishlist,name="wishlist"),
    path('wishlsit/add/<slug:product_slug>/', viewwishlist.add_to_wishlist, name='add to wishlist'),
     path('cart/remove/<int:item_id>/<int:type>', viewcart.remove_from_cart, name='remove_from_cart'),
       path('forgot-password/', viewforgotpass.forgot_password, name='forgot_password'),
           path('reset-password/', viewforgotpass.reset_password, name='reset_password'),
            path('verify-otp/', viewforgotpass.verify_otp, name='verify_otp'),]