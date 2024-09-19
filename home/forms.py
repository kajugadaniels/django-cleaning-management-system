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
        fields = ['description']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class TaskForm(forms.Form):
    name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))

class AdminApproveCleanupRequestForm(forms.ModelForm):
    class Meta:
        model = CleanupRequest
        fields = ['company']
        
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(AdminApproveCleanupRequestForm, self).__init__(*args, **kwargs)
        self.fields['company'].label = "Assign Company"