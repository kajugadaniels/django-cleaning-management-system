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
                user = User.objects.get(id=user_id).order_by('-created_at')
                if not user.is_staff:
                    user.delete()
                    messages.success(request, "User deleted successfully.")
                else:
                    messages.error(request, "You cannot delete a user with the 'is_staff' role.")
            except User.DoesNotExist:
                messages.error(request, "User not found.")

    # Manager users can only see users they added
    if request.user.role == 'Manager':
        getUsers = User.objects.filter(added_by=request.user).order_by('-created_at')
    # Admin and superusers can see all users
    elif request.user.role == 'Admin' or request.user.is_superuser:
        getUsers = User.objects.all().order_by('-created_at')
    else:
        getUsers = User.objects.none().order_by('-created_at')

    context = {
        'getUsers': getUsers,
        'logged_in_user': request.user
    }

    return render(request, 'users/index.html', context)

@login_required
def addUser(request):
    if request.user.role not in ['Admin', 'Manager'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    # For 'Manager' users, they should only be able to add 'Cleaner' users
    if request.user.role == 'Manager':
        roles = ['Cleaner']
    else:
        roles = ['Admin', 'Manager', 'Client', 'Cleaner'] if request.user.role == 'Admin' or request.user.is_superuser else ['Manager']

    if request.method == 'POST':
        form = UserCreationForm(request.POST, roles=roles)

        if form.is_valid():
            required_fields = ['name', 'email', 'phone_number', 'password']
            missing_fields = [field for field in required_fields if not form.cleaned_data.get(field)]

            if missing_fields:
                messages.error(request, f"{', '.join([field.replace('_', ' ').capitalize() for field in missing_fields])} {'is' if len(missing_fields) == 1 else 'are'} required.")
            elif form.cleaned_data.get("password") != form.cleaned_data.get("password_confirmation"):
                messages.error(request, "Password does not match.")
            else:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data["password"])
                # Automatically set role to 'Cleaner' if the logged-in user is a 'Manager'
                if request.user.role == 'Manager':
                    user.role = 'Cleaner'
                user.added_by = request.user  # Link the added user to the current user
                user.save()
                messages.success(request, "User added successfully.")
                return redirect('base:getUsers')
        else:
            for error in form.errors.values():
                messages.error(request, error)

    else:
        form = UserCreationForm(roles=roles)

    context = {
        'form': form,
        'logged_in_user': request.user
    }
    return render(request, 'users/create.html', context)

@login_required
def editUser(request, id):
    if request.user.role == 'Manager':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    user = User.objects.get(id=id)
    roles = ['Admin', 'Manager', 'Client', 'Cleaner'] if request.user.role == 'Admin' or request.user.is_superuser else ['Manager']

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user, roles=roles)

        if form.is_valid():
            required_fields = ['name', 'email', 'phone_number', 'role']
            missing_fields = [field for field in required_fields if not form.cleaned_data.get(field)]

            if missing_fields:
                messages.error(request, f"{', '.join([field.replace('_', ' ').capitalize() for field in missing_fields])} {'is' if len(missing_fields) == 1 else 'are'} required.")
            elif form.cleaned_data.get("role") not in roles:
                messages.error(request, "Invalid role selected.")
            else:
                form.save()
                messages.success(request, "User updated successfully.")
                return redirect('base:getUsers')
        else:
            for error in form.errors.values():
                messages.error(request, error)

    else:
        form = UserUpdateForm(instance=user, roles=roles)

    context = {
        'form': form,
        'logged_in_user': request.user,
        'user': user
    }
    return render(request, 'users/edit.html', context)

@login_required
def deleteUser(request, id):
    if request.user.role == 'Manager':
        messages.error(request, "You are not authorized to delete a user.")
        return redirect('base:getUsers')

    user = User.objects.filter(id=id, is_staff=False).first()

    if user:
        user.delete()
        messages.success(request, "User deleted successfully.")
    else:
        messages.error(request, "User not found or action not authorized.")

    return redirect('base:getUsers')

@login_required
def getCleanupRequests(request):
    # Ensure user is either Admin, Client, or SuperAdmin
    if request.user.role not in ['Admin', 'Manager'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    # Fetch cleanup requests based on the user role
    if request.user.role == 'Client':
        # Client users only see their own requests
        cleanupRequests = CleanupRequest.objects.filter(client=request.user, delete_status=False).select_related('manager').prefetch_related('tasks')
    elif request.user.role == 'Admin' or request.user.is_superuser:
        # Admin or SuperAdmin users see all requests
        cleanupRequests = CleanupRequest.objects.filter(delete_status=False).select_related('client', 'manager').prefetch_related('tasks')
    else:
        # Other roles should see none
        cleanupRequests = CleanupRequest.objects.none()

    # Pass the cleanup requests to the template
    context = {
        'cleanupRequests': cleanupRequests,
        'logged_in_user': request.user
    }

    return render(request, 'cleanuprequest/index.html', context)