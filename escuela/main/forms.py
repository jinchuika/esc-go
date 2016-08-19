from django import forms
from django.forms import ModelForm
from main.models import *
import datetime
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

class ProfileModelForm(ModelForm):
	class Meta:
		model = Profile
		fields = '__all__'

class UserModelForm(ModelForm):
	class Meta:
		model = User
		fields = ['username', 'password', 'first_name', 'last_name']

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		model = User
		fields = ['username', 'password', 'email', 'first_name', 'last_name']

class asd(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		model = User
		fields = ['username', 'password']

class LoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("This account is inactive."),
                code='inactive',
            )
