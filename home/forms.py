import re
from django import forms
from home.models import *
from account.models import *
from datetime import date, timedelta
from django.core.exceptions import ValidationError

class UserCreationForm(forms.ModelForm):
    firstname = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="First Name"
    )
    lastname = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Last Name"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password Confirmation"
    )
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Address"
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Gender"
    )

    class Meta:
        model = User
        fields = ['email', 'nid', 'phone_number', 'dob', 'profession', 'role', 'gender', 'address', 'password']
        widgets = {
            'nid': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        roles = kwargs.pop('roles', [])
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'required': 'true',
            'type': 'email'
        })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control',
            'required': 'true',
            'type': 'number'
        })
        self.fields['profession'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].choices = [(role, role) for role in roles]
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})

    def clean_phone_number(self):
        """
        Validates that the phone number starts with 078, 072, or 073 and is exactly 10 digits long.
        """
        phone_number = self.cleaned_data.get('phone_number')
        pattern = re.compile(r'^(078|072|073)\d{7}$')
        if not pattern.match(phone_number):
            raise ValidationError("Phone number must start with 078, 072, or 073 and be exactly 10 digits long.")
        return phone_number

    def clean_dob(self):
        """
        Validates that the user is at least 18 years old.
        """
        dob = self.cleaned_data.get('dob')
        if dob:
            today = timezone.now().date()
            age = today - dob
            if age < timedelta(days=18*365):
                raise ValidationError("User must be at least 18 years old.")
        return dob

    def clean(self):
        """
        Ensures that the password and password_confirmation fields match and sets the name.
        """
        cleaned_data = super(UserCreationForm, self).clean()
        firstname = cleaned_data.get("firstname")
        lastname = cleaned_data.get("lastname")
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if firstname and lastname:
            cleaned_data['name'] = f"{firstname} {lastname}"  # Combine into name

        if password and password_confirmation:
            if password != password_confirmation:
                self.add_error('password_confirmation', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        """
        Saves the user instance with the combined name and hashed password.
        """
        user = super(UserCreationForm, self).save(commit=False)
        user.name = self.cleaned_data.get('name')
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    firstname = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="First Name"
    )
    lastname = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Last Name"
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Gender"
    )
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Address"
    )

    class Meta:
        model = User
        fields = ['email', 'nid', 'phone_number', 'dob', 'profession', 'image', 'role', 'gender', 'address']
        widgets = {
            'nid': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        roles = kwargs.pop('roles', [])  # Pop 'roles' before calling super
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.name:
            name_parts = self.instance.name.split()
            self.fields['firstname'].initial = name_parts[0]
            self.fields['lastname'].initial = " ".join(name_parts[1:]) if len(name_parts) > 1 else ''
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'required': 'true',
            'type': 'email'
        })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control',
            'required': 'true',
            'type': 'number'
        })
        self.fields['profession'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].choices = [(role, role) for role in roles]
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})

    def clean_phone_number(self):
        """
        Validates that the phone number starts with 078, 072, or 073 and is exactly 10 digits long.
        """
        phone_number = self.cleaned_data.get('phone_number')
        pattern = re.compile(r'^(078|072|073)\d{7}$')
        if not pattern.match(phone_number):
            raise ValidationError("Phone number must start with 078, 072, or 073 and be exactly 10 digits long.")
        return phone_number

    def clean_dob(self):
        """
        Validates that the user is at least 18 years old.
        """
        dob = self.cleaned_data.get('dob')
        if dob:
            today = timezone.now().date()
            age = today - dob
            if age < timedelta(days=18*365):
                raise ValidationError("User must be at least 18 years old.")
        return dob

    def clean(self):
        """
        Ensures that the firstname and lastname fields are present and sets the full name.
        """
        cleaned_data = super().clean()
        firstname = cleaned_data.get("firstname")
        lastname = cleaned_data.get("lastname")

        if firstname and lastname:
            cleaned_data['name'] = f"{firstname} {lastname}"
        else:
            raise forms.ValidationError("Both first name and last name are required.")

        return cleaned_data

    def save(self, commit=True):
        """
        Saves the user instance with the combined name.
        """
        user = super(UserUpdateForm, self).save(commit=False)
        user.name = f"{self.cleaned_data['firstname']} {self.cleaned_data['lastname']}"
        if commit:
            user.save()
        return user

class CleanupRequestForm(forms.ModelForm):
    class Meta:
        model = CleanupRequest
        fields = ['client', 'description', 'requested_at']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'requested_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CleanupRequestForm, self).__init__(*args, **kwargs)

        if user:
            if user.role == 'Client':
                # Set the client field to the logged-in user's ID and add a readonly class
                self.fields['client'].queryset = User.objects.filter(id=user.id)
                self.fields['client'].initial = user.id
                self.fields['client'].widget.attrs['class'] += ' readonly-field'  # Add custom CSS class
            elif user.role == 'Admin' or user.is_superuser:
                # Allow only users with the 'Client' role to be selectable
                self.fields['client'].queryset = User.objects.filter(role='Client')
                self.fields['client'].label = "Choose Client"

class TaskForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))

class AdminApproveCleanupRequestForm(forms.ModelForm):
    class Meta:
        model = CleanupRequest
        fields = ['supervisor']
        
        widgets = {
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AdminApproveCleanupRequestForm, self).__init__(*args, **kwargs)
        # Only show users with the 'Supervisor' role in the Supervisor field
        self.fields['supervisor'].queryset = User.objects.filter(role='Supervisor')
        self.fields['supervisor'].label = "Assign Supervisor"

class TaskCleanerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Get the logged-in user from the view
        super(TaskCleanerForm, self).__init__(*args, **kwargs)
        # Filter cleaners added by the logged-in Supervisor user
        self.fields['cleaners'].queryset = User.objects.filter(role='Cleaner')

    cleaners = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # Default to none, will be populated in __init__
        widget=forms.CheckboxSelectMultiple, 
        required=True
    )

    class Meta:
        model = Task
        fields = ['cleaners']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'invoice_date', 'due_date', 'amount', 'file', 'is_paid']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'invoice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_paid': forms.CheckboxInput(),
        }

class WeeklyReportForm(forms.ModelForm):
    class Meta:
        model = WeeklyReport
        fields = ['supervisor', 'file', 'description']
        widgets = {
            'supervisor': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }