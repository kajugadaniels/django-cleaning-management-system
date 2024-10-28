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
    # if request.user.role not in ['Admin', 'Supervisor'] and not request.user.is_superuser:
    #     messages.error(request, "You are not authorized to access this page.")
    #     return redirect('base:dashboard')

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

    # Supervisor users can only see users they added
    if request.user.role == 'Supervisor':
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
    # if request.user.role not in ['Admin', 'Supervisor'] and not request.user.is_superuser:
    #     messages.error(request, "You are not authorized to access this page.")
    #     return redirect('base:dashboard')

    # For 'Supervisor' users, they should only be able to add 'Cleaner' users
    if request.user.role == 'Supervisor':
        roles = ['Cleaner']
    else:
        roles = ['Admin', 'Supervisor', 'Client', 'Cleaner'] if request.user.role == 'Admin' or request.user.is_superuser else ['Supervisor']

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
                # Automatically set role to 'Cleaner' if the logged-in user is a 'Supervisor'
                if request.user.role == 'Supervisor':
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
    # if request.user.role == 'Supervisor':
    #     messages.error(request, "You are not authorized to access this page.")
    #     return redirect('base:dashboard')

    user = User.objects.get(id=id)
    roles = ['Admin', 'Supervisor', 'Client', 'Cleaner'] if request.user.role == 'Admin' or request.user.is_superuser else ['Supervisor']

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
    # if request.user.role == 'Supervisor':
    #     messages.error(request, "You are not authorized to delete a user.")
    #     return redirect('base:getUsers')

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
    # if request.user.role not in ['Admin', 'Supervisor', 'Client'] and not request.user.is_superuser:
    #     messages.error(request, "You are not authorized to access this page.")
    #     return redirect('base:dashboard')

    # Fetch cleanup requests based on the user role
    if request.user.role == 'Client':
        # Client users only see their own requests
        cleanupRequests = CleanupRequest.objects.filter(client=request.user, delete_status=False).select_related('supervisor').prefetch_related('tasks').order_by('-created_at')
    elif request.user.role == 'Admin' or request.user.is_superuser:
        # Admin or SuperAdmin users see all requests
        cleanupRequests = CleanupRequest.objects.filter(delete_status=False).select_related('client', 'supervisor').prefetch_related('tasks').order_by('-created_at')
    elif request.user.role == 'Supervisor':
        # Client users only see their own requests
        cleanupRequests = CleanupRequest.objects.filter(supervisor=request.user, delete_status=False).select_related('client').prefetch_related('tasks').order_by('-created_at')
    else:
        # Other roles should see none
        cleanupRequests = CleanupRequest.objects.none()

    # Pass the cleanup requests to the template
    context = {
        'cleanupRequests': cleanupRequests,
        'logged_in_user': request.user
    }

    return render(request, 'cleanuprequest/index.html', context)

@login_required
def addCleanupRequest(request):
    if request.method == 'POST':
        cleanup_request_form = CleanupRequestForm(request.POST, request.FILES)

        task_names = request.POST.getlist('task_name[]')

        if cleanup_request_form.is_valid():
            cleanup_request = cleanup_request_form.save(commit=False)
            cleanup_request.save()

            for name in task_names:
                name = name.strip()
                if name:
                    Task.objects.create(
                        cleanup_request=cleanup_request,
                        name=name,
                        added_by=request.user
                    )

            messages.success(request, "Cleanup request created successfully with its associated tasks.")
            return redirect('base:getCleanupRequests')
        else:
            messages.error(request, "Error submitting the form. Please try again.")
    else:
        cleanup_request_form = CleanupRequestForm()

    context = {
        'cleanup_request_form': cleanup_request_form,
    }
    return render(request, 'cleanuprequest/create.html', context)

@login_required
def viewCleanupRequest(request, cleanup_request_id):
    try:
        # Fetch the cleanup request and its related tasks
        cleanupRequest = CleanupRequest.objects.select_related('client', 'Supervisor').prefetch_related('tasks').get(id=cleanup_request_id, delete_status=False)
    except CleanupRequest.DoesNotExist:
        messages.error(request, "Cleanup request not found.")
        return redirect('cleanup:getCleanupRequests')

    # Ensure only authorized users can view the details
    if request.user.role == 'Client' and cleanupRequest.client != request.user:
        messages.error(request, "You are not authorized to view this cleanup request.")
        return redirect('base:dashboard')
    # elif request.user.role not in ['Admin', 'Supervisor'] and not request.user.is_superuser:
    #     messages.error(request, "You are not authorized to access this page.")
    #     return redirect('base:dashboard')

    context = {
        'cleanupRequest': cleanupRequest,
        'tasks': cleanupRequest.tasks.all(),
        'logged_in_user': request.user
    }

    return render(request, 'cleanuprequest/show.html', context)

@login_required
def adminApproveCleanupRequest(request, request_id):
    # Ensure only Admin or SuperAdmin users can access this
    # if request.user.role not in ['Admin'] and not request.user.is_superuser:
    #     messages.error(request, "You are not authorized to access this page.")
    #     return redirect('base:dashboard')

    # Get the cleanup request
    cleanupRequest = get_object_or_404(CleanupRequest, pk=request_id)

    # Handle form submission
    if request.method == 'POST':
        form = AdminApproveCleanupRequestForm(request.POST, instance=cleanupRequest)
        
        if form.is_valid():
            # Check which button was pressed (Approve or Reject)
            if 'approve' in request.POST:
                cleanupRequest = form.save(commit=False)
                cleanupRequest.approved_at = timezone.now()  # Automatically set approval date
                cleanupRequest.status = 'Approved'  # Automatically mark as approved
                cleanupRequest.save()
                messages.success(request, "Cleanup request approved and Supervisor assigned successfully.")
            elif 'reject' in request.POST:
                cleanupRequest.status = 'Rejected'  # Mark request as rejected
                cleanupRequest.save()
                messages.success(request, "Cleanup request rejected.")
            
            return redirect('base:getCleanupRequests')
    else:
        form = AdminApproveCleanupRequestForm(instance=cleanupRequest)

    context = {
        'cleanupRequest': cleanupRequest,
        'form': form
    }

    return render(request, 'cleanuprequest/approve.html', context)

@login_required
def assignCleanersToTask(request, taskId):
    # if request.user.role not in ['Admin', 'Supervisor'] and not request.user.is_superuser:
    #     messages.error(request, "You are not authorized to access this page.")
    #     return redirect('base:dashboard')

    task = get_object_or_404(Task, id=taskId, cleanup_request__Supervisor=request.user, delete_status=False)

    if request.method == 'POST':
        form = TaskCleanerForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_at = timezone.now()  # Set the assigned_at field to the current time
            task.save()
            form.save_m2m()  # Save many-to-many data for cleaners
            messages.success(request, "Cleaners assigned successfully and time recorded.")
            return redirect('base:viewCleanupRequest', cleanup_request_id=task.cleanup_request.id)
    else:
        form = TaskCleanerForm(instance=task, user=request.user)

    context = {
        'form': form,
        'task': task,
        'cleanupRequest': task.cleanup_request
    }

    return render(request, 'tasks/create.html', context)

@login_required
def markCleanupRequestComplete(request, cleanup_request_id):
    # Ensure the user is a Client
    # if request.user.role not in ['Admin', 'Client'] and not request.user.is_superuser:
    #     messages.error(request, "You are not authorized to complete this request.")
    #     return redirect('base:getCleanupRequests')

    # Retrieve the cleanup request and associated tasks
    cleanupRequest = get_object_or_404(CleanupRequest, id=cleanup_request_id, client=request.user, delete_status=False)
    tasks = Task.objects.filter(cleanup_request=cleanupRequest, delete_status=False)

    # If the request method is POST, update the 'completed_at' fields
    if request.method == 'POST':
        # Mark the cleanup request as completed
        cleanupRequest.completed_at = timezone.now()
        cleanupRequest.save()

        # Mark all tasks as completed
        tasks.update(completed_at=timezone.now())

        messages.success(request, "Cleanup request and tasks marked as completed.")
        return redirect('base:getCleanupRequests')

    context = {
        'cleanupRequest': cleanupRequest,
        'tasks': tasks,
    }

    return render(request, 'cleanuprequest/complete.html', context)