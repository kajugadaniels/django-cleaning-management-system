from home.forms import *
from home.models import *
from account.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@login_required
def getUsers(request):
    if request.user.role not in ['Admin', 'Company'] and not request.user.is_superuser:
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

    # Company users can only see users they added
    if request.user.role == 'Company':
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

@login_required
def addUser(request):
    if request.user.role not in ['Admin', 'Company'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    # For 'Company' users, they should only be able to add 'Cleaner' users
    if request.user.role == 'Company':
        roles = ['Cleaner']
    else:
        roles = ['Admin', 'Company', 'Client', 'Cleaner'] if request.user.role == 'Admin' or request.user.is_superuser else ['Company']

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
                # Automatically set role to 'Cleaner' if the logged-in user is a 'Company'
                if request.user.role == 'Company':
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
    if request.user.role == 'Company':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    user = User.objects.get(id=id)
    roles = ['Admin', 'Company', 'Client', 'Cleaner'] if request.user.role == 'Admin' or request.user.is_superuser else ['Company']

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
    if request.user.role == 'Company':
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
    if request.user.role not in ['Admin', 'Client'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    # Retrieve cleanup requests based on user role
    if request.user.role == 'Client':
        cleanupRequests = CleanupRequest.objects.filter(client=request.user, delete_status=False).select_related('company').prefetch_related('tasks')
    elif request.user.role == 'Admin' or request.user.is_superuser:
        cleanupRequests = CleanupRequest.objects.filter(delete_status=False).select_related('client', 'company').prefetch_related('tasks')
    else:
        cleanupRequests = CleanupRequest.objects.none()

    context = {
        'cleanupRequests': cleanupRequests,
        'logged_in_user': request.user
    }

    return render(request, 'cleanup_requests/index.html', context)

@login_required
def addCleanupRequest(request):
    if request.user.role != 'Client':
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    if request.method == 'POST':
        cleanup_request_form = CleanupRequestForm(request.POST)
        task_formset = TaskFormSet(request.POST)
        
        if cleanup_request_form.is_valid() and task_formset.is_valid():
            cleanup_request = cleanup_request_form.save(commit=False)
            cleanup_request.client = request.user  # Auto-fill client
            cleanup_request.save()
            
            task_formset.instance = cleanup_request
            task_formset.save()
            
            messages.success(request, "Cleanup request created successfully.")
            return redirect('base:getCleanupRequests')
    else:
        cleanup_request_form = CleanupRequestForm()
        task_formset = TaskFormSet()

    context = {
        'cleanup_request_form': cleanup_request_form,
        'task_formset': task_formset
    }
    return render(request, 'cleanup_requests/create.html', context)

@login_required
def editCleanupRequest(request, id):
    if request.user.role not in ['Admin', 'Client'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    cleanupRequest = get_object_or_404(CleanupRequest, id=id)

    if request.method == 'POST':
        form = CleanupRequestForm(request.POST, instance=cleanupRequest)
        if form.is_valid():
            form.save()
            messages.success(request, "Cleanup request updated successfully.")
            return redirect('base:getCleanupRequests')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CleanupRequestForm(instance=cleanupRequest)

    context = {
        'form': form,
        'logged_in_user': request.user,
        'cleanupRequest': cleanupRequest
    }
    return render(request, 'cleanup_requests/edit.html', context)

@login_required
def deleteCleanupRequest(request, id):
    if request.user.role not in ['Admin', 'Client'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    cleanupRequest = get_object_or_404(CleanupRequest, id=id)
    if request.method == 'POST':
        cleanupRequest.delete_status = True
        cleanupRequest.save()
        messages.success(request, "Cleanup request deleted successfully.")
        return redirect('base:getCleanupRequests')
    
    return render(request, 'cleanup_requests/delete.html', {'cleanupRequest': cleanupRequest})

@login_required
def getTasks(request):
    if request.user.role not in ['Admin', 'Client'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        if task_id:
            try:
                task = Task.objects.get(id=task_id)
                if not task.delete_status:
                    task.delete_status = True
                    task.save()
                    messages.success(request, "Task deleted successfully.")
                else:
                    messages.error(request, "Task is already deleted.")
            except Task.DoesNotExist:
                messages.error(request, "Task not found.")

    if request.user.role == 'Client':
        tasks = Task.objects.filter(cleanup_request__client=request.user)
    elif request.user.role == 'Admin' or request.user.is_superuser:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.none()

    context = {
        'tasks': tasks,
        'logged_in_user': request.user
    }

    return render(request, 'tasks/index.html', context)

@login_required
def addTask(request):
    if request.user.role not in ['Admin', 'Client'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.added_by = request.user
            task.save()
            messages.success(request, "Task added successfully.")
            return redirect('base:getTasks')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = TaskForm()

    context = {
        'form': form,
        'logged_in_user': request.user
    }
    return render(request, 'tasks/create.html', context)

@login_required
def editTask(request, id):
    if request.user.role not in ['Admin', 'Client'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    task = get_object_or_404(Task, id=id)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully.")
            return redirect('base:getTasks')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = TaskForm(instance=task)

    context = {
        'form': form,
        'logged_in_user': request.user,
        'task': task
    }
    return render(request, 'tasks/edit.html', context)

@login_required
def deleteTask(request, id):
    if request.user.role not in ['Admin', 'Client'] and not request.user.is_superuser:
        messages.error(request, "You are not authorized to access this page.")
        return redirect('base:dashboard')

    task = get_object_or_404(Task, id=id)
    if request.method == 'POST':
        task.delete_status = True
        task.save()
        messages.success(request, "Task deleted successfully.")
        return redirect('base:getTasks')
    
    return render(request, 'tasks/delete.html', {'task': task})