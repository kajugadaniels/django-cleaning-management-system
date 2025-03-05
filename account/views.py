import random
import logging
from account.forms import *
from account.utils import *
from account.models import *
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
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
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profil mis à jour avec succès.')
                return redirect('auth:userProfile')
            else:
                password_form = PasswordChangeForm(user=user)
        elif 'password_form' in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Mot de passe modifié avec succès. Veuillez vous reconnecter.')
                logout(request)
                return redirect('auth:login')
            else:
                profile_form = UserProfileForm(instance=user)
    else:
        profile_form = UserProfileForm(instance=user)
        password_form = PasswordChangeForm(user=user)

    context = {
        'profile_form': profile_form,
        'password_form': password_form
    }

    return render(request, 'auth/profile.html', context)

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, _("User with this email does not exist."))
                return redirect('auth:forgetPassword')
            
            # Generate OTP and update user instance
            otp = generate_otp()
            user.reset_otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            
            # Prepare email content
            subject = 'Password Reset OTP'
            message = f'Your password reset OTP is: {otp}'
            recipient_list = [user.email]
            
            # Use the custom send_email utility
            if send_email(subject, message, recipient_list):
                messages.success(request, _("An OTP has been sent to your email address. Please check your inbox."))
                request.session['reset_email'] = email
                return redirect('auth:forgetPasswordConfirm')
            else:
                messages.error(request, _("Failed to send OTP email. Please try again later."))
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = PasswordResetRequestForm()

    context = {
        'form': form,
        'step': 'request'
    }

    return render(request, 'auth/forget-password.html', context)

def password_reset_confirm(request):
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            # Clear the OTP fields
            user.reset_otp = None
            user.otp_created_at = None
            user.save()
            messages.success(request, "Your password has been reset successfully. Please log in with your new password.")
            # Remove the email from session after successful reset
            request.session.pop('reset_email', None)
            return redirect('auth:login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # Retrieve the email from session and set it as initial data
        email = request.session.get('reset_email', '')
        form = PasswordResetConfirmForm(initial={'email': email})
    context = {
        'form': form,
        'step': 'confirm'
    }

    return render(request, 'auth/forget-password.html', context)