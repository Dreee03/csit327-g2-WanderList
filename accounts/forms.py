from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomUserCreationForm(forms.Form):
    # Manually define all fields, including email which was in the Meta block
    username = forms.CharField(
        label='Username',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email'
        })
    )
    password = forms.CharField( # Changed from password1 for cleaner access in view
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter password'
        })
    )

    # Add clean method for password confirmation (essential form logic)
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError(
                "Passwords do not match."
            )
        return cleaned_data


class CustomAuthenticationForm(forms.Form):
    # Keep the field definitions as they are, but inherit from forms.Form
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )

class SupabaseUser:
    """Mimics django.contrib.auth.models.User for template compatibility."""
    def __init__(self, username, is_authenticated=True):
        self.username = username
        self.is_authenticated = is_authenticated
        
    def __str__(self):
        return self.username
    
    # Required for compatibility with certain Django internals
    def is_anonymous(self):
        return not self.is_authenticated
    def is_staff(self):
        return False