from django import forms
from django.core.validators import RegexValidator

class CustomUserCreationForm(forms.Form):
    # Manually define all fields, including email which was in the Meta block
    username = forms.CharField(
        label='Username',
        min_length=3,
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_\.\-]+$',
                message='Username may contain letters, numbers, underscores, dots, and dashes only.'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username',
            'autocomplete': 'username',
            'required': 'required'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email',
            'autocomplete': 'email',
            'required': 'required'
        })
    )
    password = forms.CharField( # Changed from password1 for cleaner access in view
        label="Password",
        min_length=8,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d).+$',
                message='Password must contain at least one letter and one number.'
            )
        ],
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'new-password',
            'required': 'required'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter password',
            'autocomplete': 'new-password',
            'required': 'required'
        })
    )

    # Add clean method for password confirmation (essential form logic)
    def clean(self):
        cleaned_data = super().clean()
        # Normalize inputs
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if username:
            cleaned_data["username"] = username.strip()
        if email:
            cleaned_data["email"] = email.strip().lower()

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class CustomAuthenticationForm(forms.Form):
    # Keep the field definitions as they are, but inherit from forms.Form
    username = forms.CharField(
        min_length=3,
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username',
            'autocomplete': 'username',
            'required': 'required'
        })
    )
    password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'current-password',
            'required': 'required'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username:
            cleaned_data['username'] = username.strip()
        if not username or not password:
            raise forms.ValidationError('Both username and password are required.')
        return cleaned_data

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