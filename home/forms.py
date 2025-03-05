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
        label="First Name",
        required=False
    )
    lastname = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Last Name",
        required=False
    )
    company_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Company Name",
        required=False
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password",
        required=True
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password Confirmation",
        required=True
    )
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Address",
        required=False
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Gender",
        required=False
    )

    class Meta:
        model = User
        fields = ['email', 'nid', 'phone_number', 'dob', 'profession', 'role', 'gender', 'address', 'password']
        widgets = {
            'nid': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        roles = kwargs.pop('roles', [])
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'type': 'email'
        })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control',
            'type': 'number'
        })
        self.fields['profession'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].choices = [(role, role) for role in roles]
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['company_name'].widget.attrs.update({'class': 'form-control'})

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            pattern = re.compile(r'^(078|072|073)\d{7}$')
            if not pattern.match(phone_number):
                raise ValidationError("Phone number must start with 078, 072, or 073 and be exactly 10 digits long.")
        return phone_number

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob:
            today = timezone.now().date()
            age = today - dob
            if age < timedelta(days=18*365):
                raise ValidationError("User must be at least 18 years old.")
        return dob

    def clean(self):
        cleaned_data = super(UserCreationForm, self).clean()
        role = cleaned_data.get("role")
        firstname = cleaned_data.get("firstname")
        lastname = cleaned_data.get("lastname")
        company_name = cleaned_data.get("company_name")
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if role == 'Client':
            if not company_name:
                self.add_error('company_name', "Company name is required for Client role.")
            cleaned_data['name'] = company_name
        else:
            if not firstname or not lastname:
                raise forms.ValidationError("Both first name and last name are required for this role.")
            cleaned_data['name'] = f"{firstname} {lastname}"

        if password and password_confirmation:
            if password != password_confirmation:
                self.add_error('password_confirmation', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
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
        label="First Name",
        required=False
    )
    lastname = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Last Name",
        required=False
    )
    company_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Company Name",
        required=False
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Gender",
        required=False
    )
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Address",
        required=False
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password",
        required=False
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password Confirmation",
        required=False
    )

    class Meta:
        model = User
        fields = ['email', 'nid', 'phone_number', 'dob', 'profession', 'image', 'role', 'gender', 'address']
        widgets = {
            'nid': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        roles = kwargs.pop('roles', [])
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.name:
            if self.instance.role == 'Client':
                self.fields['company_name'].initial = self.instance.name
            else:
                name_parts = self.instance.name.split()
                self.fields['firstname'].initial = name_parts[0]
                self.fields['lastname'].initial = " ".join(name_parts[1:]) if len(name_parts) > 1 else ''
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'type': 'email'
        })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control',
            'type': 'number'
        })
        self.fields['profession'].widget.attrs.update({'class': 'form-control'})
        self.fields['role'].choices = [(role, role) for role in roles]
        self.fields['role'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['company_name'].widget.attrs.update({'class': 'form-control'})

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            pattern = re.compile(r'^(078|072|073)\d{7}$')
            if not pattern.match(phone_number):
                raise ValidationError("Phone number must start with 078, 072, or 073 and be exactly 10 digits long.")
        return phone_number

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob:
            today = timezone.now().date()
            age = today - dob
            if age < timedelta(days=18*365):
                raise ValidationError("User must be at least 18 years old.")
        return dob

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        firstname = cleaned_data.get("firstname")
        lastname = cleaned_data.get("lastname")
        company_name = cleaned_data.get("company_name")
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if role == 'Client':
            if not company_name:
                self.add_error('company_name', "Company name is required for Client role.")
            cleaned_data['name'] = company_name
        else:
            if not firstname or not lastname:
                raise forms.ValidationError("Both first name and last name are required for this role.")
            cleaned_data['name'] = f"{firstname} {lastname}"

        if password or password_confirmation:
            if password != password_confirmation:
                self.add_error('password_confirmation', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super(UserUpdateForm, self).save(commit=False)
        user.name = self.cleaned_data.get('name')
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
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
            elif user.role == 'Manager' or user.is_superuser:
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
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Store 'user' as an instance attribute
        super(WeeklyReportForm, self).__init__(*args, **kwargs)

        if self.user:
            if self.user.role == 'Supervisor':
                # Set the supervisor field to the logged-in user's ID and make it readonly
                self.fields['supervisor'].queryset = User.objects.filter(id=self.user.id)
                self.fields['supervisor'].initial = self.user.id
                self.fields['supervisor'].widget.attrs['class'] += ' readonly-field'  # Add custom CSS class
                self.fields['supervisor'].widget.attrs['readonly'] = True  # HTML readonly attribute
                self.fields['supervisor'].required = False  # Will set in clean_supervisor method
            elif self.user.role == 'Manager' or self.user.is_superuser:
                # Allow only users with the 'Supervisor' role to be selectable
                self.fields['supervisor'].queryset = User.objects.filter(role='Supervisor')
                self.fields['supervisor'].label = "Choose Supervisor"
                self.fields['supervisor'].required = True  # Ensure it's required

    def clean_supervisor(self):
        """
        Ensures that Supervisors cannot change the supervisor field and Managers/Superusers must select a supervisor.
        """
        supervisor = self.cleaned_data.get('supervisor')
        user = self.user  # Access the stored user

        if user:
            if user.role == 'Supervisor':
                # For Supervisors, ensure the supervisor is themselves
                if supervisor != user:
                    raise ValidationError("Supervisors can only assign themselves as supervisors.")
                return user  # Return the logged-in user
            elif user.role == 'Manager' or user.is_superuser:
                # For Managers/Superusers, ensure a supervisor is selected
                if not supervisor:
                    raise ValidationError("Supervisor is required.")
                return supervisor
        return supervisor

    def clean(self):
        """
        Additional cleaning if necessary.
        """
        cleaned_data = super().clean()
        # Any additional cleaning can be done here
        return cleaned_data

    def save(self, commit=True):
        """
        Saves the WeeklyReport instance, ensuring supervisor field integrity.
        """
        weekly_report = super(WeeklyReportForm, self).save(commit=False)
        user = self.user

        if user and user.role == 'Supervisor':
            # Ensure supervisor is set to the logged-in user
            weekly_report.supervisor = user

        if commit:
            weekly_report.save()
        return weekly_report