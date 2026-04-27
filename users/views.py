"""
Users app views for authentication and dashboard.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import User

def login_view(request):
    """Login view with role selection."""
    if request.user.is_authenticated:
        return redirect('users:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(request, 'This account has been disabled.')
                return render(request, 'users/login.html')

            # Superuser can choose any role
            if user.is_superuser:
                if selected_role:
                    # Store role choice in session for later use
                    request.session['selected_role'] = selected_role
                    login(request, user)
                    return redirect('users:dashboard')
                else:
                    # Show role selection for superuser
                    return render(request, 'users/login.html', {
                        'user': user,
                        'show_role_selection': True
                    })
            else:
                # Regular user must match their actual role
                if user.role != selected_role:
                    messages.error(request, f'You must select your correct role ({user.get_role_display()}).')
                    return render(request, 'users/login.html')

                request.session['selected_role'] = user.role
                login(request, user)
                return redirect('users:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')

def logout_view(request):
    """Logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:login')

@login_required
def dashboard(request):
    """Dashboard redirect based on role."""
    selected_role = request.session.get('selected_role', request.user.role)

    # Redirect to appropriate dashboard
    if selected_role == 'cashier':
        from sales.views import cashier_dashboard
        return cashier_dashboard(request)
    elif selected_role in ['manager', 'inventory'] or request.user.is_superuser:
        from inventory.views import manager_dashboard
        return manager_dashboard(request)
    else:
        from sales.views import cashier_dashboard
        return cashier_dashboard(request)

@login_required
@require_http_methods(["GET", "POST"])
def manage_passwords(request):
    """Manage user passwords - managers only."""
    if not request.user.can_manage_users():
        messages.error(request, 'You do not have permission to manage user passwords.')
        return redirect('dashboard')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not user_id:
            messages.error(request, 'Please select a user.')
            return render(request, 'users/manage_passwords.html', {
                'users': User.objects.filter(is_active=True)
            })

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return render(request, 'users/manage_passwords.html', {
                'users': User.objects.filter(is_active=True)
            })

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/manage_passwords.html', {
                'users': User.objects.filter(is_active=True)
            })

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'users/manage_passwords.html', {
                'users': User.objects.filter(is_active=True)
            })

        target_user.set_password(new_password)
        target_user.save()
        messages.success(request, f'Password for {target_user.username} has been updated successfully.')

    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    return render(request, 'users/manage_passwords.html', {'users': users})

@login_required
def change_password(request, user_id):
    """Change password for a specific user."""
    if not request.user.can_manage_users():
        if request.user.id != user_id:
            messages.error(request, 'You do not have permission.')
            return redirect('dashboard')

    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('dashboard')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'users/change_password.html', {'target_user': target_user})

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'users/change_password.html', {'target_user': target_user})

        target_user.set_password(new_password)
        target_user.save()
        messages.success(request, f'Password for {target_user.username} has been updated.')
        return redirect('manage_passwords')

    return render(request, 'users/change_password.html', {'target_user': target_user})
