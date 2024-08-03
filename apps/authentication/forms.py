from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Role

class CustomUserCreationForm(UserCreationForm):
    roles = forms.MultipleChoiceField(
        choices=Role.get_role_choices(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'name', 'email', 'password1', 'password2', 'roles', 'team', 'is_active', 'is_staff', 'is_superuser')



class CustomUserChangeForm(UserChangeForm):
    roles = forms.MultipleChoiceField(
        choices=Role.get_role_choices(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'name', 'email', 'roles', 'team', 'is_active', 'is_staff', 'is_superuser')




class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Name (optional)",
                "class": "form-control"
            }
        ))
    role = forms.ChoiceField(
        choices=Role.ROLE_CHOICES, 
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'role', 'password1', 'password2')
