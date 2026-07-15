from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def login_view(request):
    if request.method == "POST":
        login_input = request.POST.get("username")  # username or email
        password = request.POST.get("password")

        # Check if the user entered an email
        if "@" in login_input:
            try:
                user_obj = User.objects.get(email__iexact=login_input)
                username = user_obj.username
            except User.DoesNotExist:
                username = login_input
        else:
            username = login_input

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid username/email or password")

    return render(request, "login.html")
def signup_view(request):
    if request.method != "POST":
        return redirect("login")

    first_name = request.POST.get("first_name")
    last_name = request.POST.get("last_name")
    username = request.POST.get("username")
    email = request.POST.get("email")
    password1 = request.POST.get("password1")
    password2 = request.POST.get("password2")

    if password1 != password2:
        messages.error(request, "Passwords do not match")
        return redirect("login")

    if User.objects.filter(username=username).exists():
        messages.error(request, "Username already exists")
        return redirect("login")

    if User.objects.filter(email=email).exists():
        messages.error(request, "Email already exists")
        return redirect("login")

    User.objects.create_user(
        username=username,
        email=email,
        password=password1,
        first_name=first_name,
        last_name=last_name,
    )

    messages.success(request, "Account created successfully")
    return redirect("login")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")