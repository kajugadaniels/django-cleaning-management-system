from urllib.request import Request
from home.forms import *
from home.models import *
from account.models import *
from django.contrib import messages
from django.db.models import Count, Q, F  # Import necessary models
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def getUsers(request):
    if request.user.role not in ['Admin', 'Manager'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                if not user.is_staff:
                    user.delete()
                    messages.success(request, "User deleted successfully.")
                else:
                    messages.error(request, "You cannot delete a user with the 'is_staff' role.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

    # Manager users can only see users they added
    if request.user.role == 'Manager':
        getUsers = User.objects.filter(added_by=request.user)
    # Admin and superusers can see all users
    elif request.user.role == 'Admin' or request.user.is_superuser:
        getUsers = User.objects.all()
    else:
        getUsers = User.objects.none()

    context = {
        'getUsers': getUsers,
        'logged_in_user': request.user
    }

    return render(request, 'users/index.html', context)