from django import forms
from home.models import *
from account.models import *

class UserCreationForm(forms.ModelForm):
    firstname = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}), label="First Name")
    lastname = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'true'}), label="Last Name")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'true'}))
    password_confirmation = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'true'}), label="Password Confirmation")

    class Meta:
        model = User
        fields = ['email', 'nid', 'phone_number', 'dob', 'profession', 'role', 'password']
        widgets = {
            'nid': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'required': 'true'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'true'}),
        }

    def __init__(self, *args, **kwargs):
        roles = kwargs.pop('roles', [])
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'required': 'true', 'type': 'email'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'required': 'true', 'type': 'number'})
        self.fields['profession'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['role'].choices = [(role, role) for role in roles]
        self.fields['role'].widget.attrs.update({'class': 'form-control', 'required': 'true'})

    def clean(self):
        cleaned_data = super(UserCreationForm, self).clean()
        firstname = cleaned_data.get("firstname")
        lastname = cleaned_data.get("lastname")
        # Ensure both firstname and lastname are present before setting the name
        if firstname and lastname:
            cleaned_data['name'] = f"{firstname} {lastname}"  # Combine into name
        return cleaned_data

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.name = self.cleaned_data.get('name')  # Ensure the name is set from cleaned_data
        if commit:
            user.save()
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'nid', 'phone_number', 'dob', 'profession', 'image', 'role']
        widgets = {
            'nid': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number', 'required': 'true'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'true'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        roles = kwargs.pop('roles', [])
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['profession'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['role'].choices = [(role, role) for role in roles]
        self.fields['role'].widget.attrs.update({'class': 'form-control', 'required': 'true'})


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