from django import forms
from home.models import *
from account.models import *

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'true'}))
    password_confirmation = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': 'true'}), label="Password Confirmation")

    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'role', 'password']

    def __init__(self, *args, **kwargs):
        roles = kwargs.pop('roles', [])
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['role'].choices = [(role, role) for role in roles]
        self.fields['role'].widget.attrs.update({'class': 'form-control', 'required': 'true'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation and password != password_confirmation:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone_number', 'image', 'role']

    def __init__(self, *args, **kwargs):
        roles = kwargs.pop('roles', [])
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['role'].choices = [(role, role) for role in roles]
        self.fields['role'].widget.attrs.update({'class': 'form-control', 'required': 'true'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})

class CleanupRequestForm(forms.ModelForm):
    class Meta:
        model = CleanupRequest
        fields = ['client', 'description']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(CleanupRequestForm, self).__init__(*args, **kwargs)
        # Only show users with the 'Client' role in the Client field
        self.fields['client'].queryset = User.objects.filter(role='Client')
        self.fields['client'].label = "Choose Client"

class TaskForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))

class AdminApproveCleanupRequestForm(forms.ModelForm):
    class Meta:
        model = CleanupRequest
        fields = ['manager']
        
        widgets = {
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AdminApproveCleanupRequestForm, self).__init__(*args, **kwargs)
        # Only show users with the 'Manager' role in the Manager field
        self.fields['manager'].queryset = User.objects.filter(role='Manager')
        self.fields['manager'].label = "Assign Manager"

class TaskCleanerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Get the logged-in user from the view
        super(TaskCleanerForm, self).__init__(*args, **kwargs)
        # Filter cleaners added by the logged-in manager user
        self.fields['cleaners'].queryset = User.objects.filter(role='Cleaner', added_by=user)

    cleaners = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # Default to none, will be populated in __init__
        widget=forms.CheckboxSelectMultiple, 
        required=True
    )

    class Meta:
        model = Task
        fields = ['cleaners']