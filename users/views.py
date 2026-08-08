from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme


def safe_next(request):
    """The ?next= target, but only if it points back into this site.

    Redirecting to an unvalidated ?next= lets an attacker send a phishing link
    that logs the victim in and then bounces them to an external lookalike.
    """
    target = request.POST.get('next') or request.GET.get('next')
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return target
    return None


def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(safe_next(request) or 'home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')


def user_register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password1 = request.POST.get('password1') or ''
        password2 = request.POST.get('password2') or ''

        errors = []
        if not username:
            errors.append('Please choose a username.')
        if not password1:
            errors.append('Please enter a password.')
        if password1 != password2:
            errors.append('Passwords do not match.')
        if username and User.objects.filter(username__iexact=username).exists():
            errors.append('Username already taken.')
        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append('Please enter a valid email address.')
        if password1 and password1 == password2:
            # AUTH_PASSWORD_VALIDATORS were configured but never actually run,
            # so "123" was an acceptable password.
            try:
                validate_password(password1, User(username=username, email=email))
            except ValidationError as exc:
                errors.extend(exc.messages)

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect(safe_next(request) or 'home')
    return render(request, 'users/register.html')


def user_logout(request):
    logout(request)
    return redirect('home')
