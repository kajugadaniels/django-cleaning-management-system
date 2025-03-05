from django import forms
from account.models import *
from datetime import timedelta
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import PasswordChangeForm

class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '**********'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password")
        return cleaned_data

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'dob', 'profession', 'image', 'role']  # Added dob and profession fields
        widgets = {
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'true'}),  # Specify DateInput widget for dob
            'image': forms.FileInput(attrs={'class': 'form-control'}),  # Ensure FileInput widget for image
        }

    def __init__(self, *args, **kwargs):
        roles = kwargs.pop('roles', [])
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['profession'].widget.attrs.update({'class': 'form-control', 'required': 'true'})  # Assuming you want the profession editable
        self.fields['role'].choices = [(role, role) for role in roles]
        self.fields['role'].widget.attrs.update({'class': 'form-control', 'required': 'true'})

class PasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}))
    class Meta:
        model = User

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label=_("Email Address"),
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("User with this email address does not exist."))
        return email

class PasswordResetConfirmForm(forms.Form):
    email = forms.EmailField(
        label=_("Email Address"),
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter your email address',
            'class': 'form-control'
        })
    )
    otp = forms.CharField(
        label=_("OTP"),
        max_length=7,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the OTP sent to your email',
            'class': 'form-control'
        })
    )
    new_password = forms.CharField(
        label=_("New Password"),
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Enter your new password',
            'class': 'form-control'
        })
    )
    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        required=True,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm your new password',
            'class': 'form-control'
        })
    )

    def __init__(self, *args, **kwargs):
        super(PasswordResetConfirmForm, self).__init__(*args, **kwargs)
        # If an initial email is provided, mark the field as readonly.
        if self.initial.get('email'):
            self.fields['email'].widget.attrs.update({'readonly': 'readonly'})

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        otp = cleaned_data.get("otp")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError(_("The two password fields must match."))

        try:
            user = User.objects.get(email=email, reset_otp=otp)
        except User.DoesNotExist:
            raise forms.ValidationError(_("Invalid OTP or email address."))

        # Check if the OTP is expired (valid for 10 minutes)
        if user.otp_created_at and timezone.now() > user.otp_created_at + timedelta(minutes=10):
            raise forms.ValidationError(_("OTP has expired. Please request a new one."))

        # Pass the user instance to the form's cleaned_data for later use
        cleaned_data['user'] = user
        return cleaned_data