from functools import wraps
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, ProfileUpdateForm


def role_required(allowed_roles):
    """Prevents a user from opening another role's dashboard by typing its URL."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, "Access denied: You are not authorized to view that dashboard.")
                return redirect('dashboard_redirect')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.status != 'Active':
                messages.error(request, "Your account is inactive. Contact the Administrator.")
                return render(request, 'accounts/login.html')
            login(request, user)
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard_redirect(request):
    """Routes each user to the dashboard matching their role."""
    if request.user.role == 'Admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'Staff':
        return redirect('staff_dashboard')
    return redirect('viewer_dashboard')


@role_required(['Admin'])
def admin_dashboard(request):
    return render(request, 'accounts/dashboard_admin.html')


@role_required(['Staff'])
def staff_dashboard(request):
    return render(request, 'accounts/dashboard_staff.html')


@role_required(['Viewer'])
def viewer_dashboard(request):
    return render(request, 'accounts/dashboard_viewer.html')


@login_required
def profile_view(request):
    """Logged-in users can only view and edit their own profile."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
        else:
            messages.error(request, "Failed to update profile. Check the fields below.")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})