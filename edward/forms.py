from django import forms
from .models import Contact, UserProfile ,PendingWork,Notification
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    message = forms.CharField(widget=forms.Textarea) 

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['user', 'message', 'tag']

class PendingWorkForm(forms.ModelForm):
    class Meta:
        model = PendingWork
        fields = ['title', 'description', 'due_date']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})  # HTML date input
        }

class ClientSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'autocomplete': 'email',
        'placeholder': 'Enter your email'
    }))

    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'autocomplete': 'given-name',
        'placeholder': 'First Name'
    }))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'autocomplete': 'family-name',
        'placeholder': 'Last Name'
    }))

    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'autocomplete': 'username',
        'placeholder': 'Create a username'
    }))

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={
        'autocomplete': 'new-password',
        'placeholder': 'Create password'
    }))

    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={
        'autocomplete': 'new-password',
        'placeholder': 'Confirm password'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

class AdminCreateUserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class ClientCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        labels = {
            'username': 'New Username',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UpdatePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Current Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm New Password"
    )




