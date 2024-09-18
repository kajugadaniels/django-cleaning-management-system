from account.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def getUsers(request):
    if request.user.role == 'Manager':
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

    if request.user.role == 'Manager':
        getUsers = User.objects.filter(role='Manager')
    elif request.user.role == 'Admin' or request.user.is_superuser:
        getUsers = User.objects.all()
    else:
        getUsers = User.objects.none()

    context = {
        'getUsers': getUsers,
        'logged_in_user': request.user
    }

    return render(request, 'users/index.html', context)

@login_required
def addUser(request):
    if request.user.role == 'Manager':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    roles = ['Admin', 'Manager', 'Finance', 'Stock Manager'] if request.user.role == 'Admin' or request.user.is_superuser else ['Manager']

    if request.method == 'POST':
        form = UserCreationForm(request.POST, roles=roles)

        # Check if form is valid first
        if form.is_valid():
            required_fields = ['name', 'email', 'phone_number', 'password', 'role']
            missing_fields = [field for field in required_fields if not form.cleaned_data.get(field)]

            if missing_fields:
                messages.error(request, f"{', '.join([field.replace('_', ' ').capitalize() for field in missing_fields])} {'is' if len(missing_fields) == 1 else 'are'} required.")
            elif form.cleaned_data.get("password") != form.cleaned_data.get("password_confirmation"):
                messages.error(request, "Password does not match.")
            elif form.cleaned_data.get("role") not in roles:
                messages.error(request, "Invalid role selected.")
            else:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data["password"])
                user.save()
                messages.success(request, "User added successfully.")
                return redirect('base:getUsers')
        else:
            # Display form errors
            for error in form.errors.values():
                messages.error(request, error)

    else:
        form = UserCreationForm(roles=roles)

    context = {
        'form': form,
        'logged_in_user': request.user
    }
    return render(request, 'users/create.html', context)