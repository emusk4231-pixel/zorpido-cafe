<<<<<<< HEAD
"""
Forms for user registration, login, and profile management
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from .models import User, CustomerMessage

class CustomerRegistrationForm(UserCreationForm):
    """
    Form for customer registration with all required fields
    """
    full_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    phone = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '98XXXXXXXX'
        })
    )
    
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Location'
        })
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'date_of_birth', 
                 'location', 'password1', 'password2']

    agree_terms = forms.BooleanField(
        required=True,
        label='I have read and agree to the Terms & Conditions',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_agree_terms'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def save(self, commit=True, request=None):
        user = super().save(commit=False)
        user.user_type = 'customer'
        # Keep username for admin compatibility; do not require separate username from customers.
        # If username empty, set to email local-part to satisfy AbstractUser constraints.
        if not user.username:
            user.username = user.email.split('@')[0]
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """
    Custom login form with email-based authentication and Bootstrap styling
    """
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def confirm_login_allowed(self, user):
        # Email verification enforcement removed: users may log in immediately after registering
        return


class StaffLoginForm(AuthenticationForm):
    """
    Login form specifically for staff/POS access
    """
    username = forms.EmailField(
        label='Staff Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Staff Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class CustomerMessageForm(forms.ModelForm):
    """
    Form for customer inquiries/messages
    """
    class Meta:
        model = CustomerMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number (Optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Message',
                'rows': 5
            }),
        }


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form with email verification
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No user with this email address exists.")
        return email


class ResetPasswordForm(forms.Form):
    """
    Form for setting new password after reset
    """
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for customers to update their profile
    """
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'date_of_birth', 'location', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email


class StaffCustomerForm(forms.ModelForm):
    """Form for staff to edit customer profiles and basic financials."""
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'date_of_birth', 'location', 'profile_picture', 'loyalty_points', 'credit_balance']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'loyalty_points': forms.NumberInput(attrs={'class': 'form-control'}),
            'credit_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class CreditAdjustmentForm(forms.Form):
    ACTION_CHOICES = (
        ('add', 'Add Credit'),
        ('deduct', 'Deduct Credit'),
        ('adjust', 'Adjustment'),
    )
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
=======
"""
Forms for user registration, login, and profile management
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.core.exceptions import ValidationError
from .models import User, CustomerMessage

class CustomerRegistrationForm(UserCreationForm):
    """
    Form for customer registration with all required fields
    """
    full_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    phone = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '98XXXXXXXX'
        })
    )
    
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    location = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Location'
        })
    )
    
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'date_of_birth', 
                 'location', 'password1', 'password2']

    agree_terms = forms.BooleanField(
        required=True,
        label='I have read and agree to the Terms & Conditions',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_agree_terms'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def save(self, commit=True, request=None):
        user = super().save(commit=False)
        user.user_type = 'customer'
        # Keep username for admin compatibility; do not require separate username from customers.
        # If username empty, set to email local-part to satisfy AbstractUser constraints.
        if not user.username:
            user.username = user.email.split('@')[0]
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """
    Custom login form with email-based authentication and Bootstrap styling
    """
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    
    def confirm_login_allowed(self, user):
        # Email verification enforcement removed: users may log in immediately after registering
        return


class StaffLoginForm(AuthenticationForm):
    """
    Login form specifically for staff/POS access
    """
    username = forms.EmailField(
        label='Staff Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Staff Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class CustomerMessageForm(forms.ModelForm):
    """
    Form for customer inquiries/messages
    """
    class Meta:
        model = CustomerMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number (Optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Message',
                'rows': 5
            }),
        }


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form with email verification
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No user with this email address exists.")
        return email


class ResetPasswordForm(forms.Form):
    """
    Form for setting new password after reset
    """
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New Password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm New Password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password1')
        password2 = cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for customers to update their profile
    """
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'date_of_birth', 'location', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email


class StaffCustomerForm(forms.ModelForm):
    """Form for staff to edit customer profiles and basic financials."""
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'date_of_birth', 'location', 'profile_picture', 'loyalty_points', 'credit_balance']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'loyalty_points': forms.NumberInput(attrs={'class': 'form-control'}),
            'credit_balance': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class CreditAdjustmentForm(forms.Form):
    ACTION_CHOICES = (
        ('add', 'Add Credit'),
        ('deduct', 'Deduct Credit'),
        ('adjust', 'Adjustment'),
    )
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01, widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
    note = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))