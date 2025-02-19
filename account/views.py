from account.forms import *
from django.contrib import messages
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash

def user_login(request):
    if request.user.is_authenticated:
        return redirect('base:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)

            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    messages.success(request, _('Login successful!'))
                    return redirect('base:dashboard')
                else:
                    messages.error(request, _('Your account is inactive.'))
            else:
                messages.error(request, _('Invalid email or password'))
        else:
            messages.error(request, _("Please correct the error below."))
    else:
        form = LoginForm()

    context = {
        'form': form
    }

    return render(request, 'auth/login.html', context)

def user_logout(request):
    logout(request)
    return redirect('auth:login')

@login_required
def userProfile(request):
    user = request.user

    if request.method == 'POST':
        if 'profile_form' in request.POST:
            profile_form = UserUpdateForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('auth:userProfile')
            else:
                # Pass errors to the template
                for error in profile_form.errors.values():
                    messages.error(request, error)

                # If there are errors in the form, we re-render it
                password_form = PasswordChangeForm(user=user)
        elif 'password_form' in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Your password has been changed successfully. Please log in again to continue.')
                logout(request)
                return redirect('auth:login')
            else:
                # Pass errors to the template
                for error in password_form.errors.values():
                    messages.error(request, error)
                profile_form = UserUpdateForm(instance=user)
    else:
        profile_form = UserUpdateForm(instance=user)
        password_form = PasswordChangeForm(user=user)

    context = {
        'profile_form': profile_form,
        'password_form': password_form
    }

    return render(request, 'auth/profile.html', context)


