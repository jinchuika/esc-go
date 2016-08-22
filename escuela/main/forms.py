from django import forms
from django.forms import ModelForm
from main.models import *
import datetime
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

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
                _("La cuenta está inactiva."),
                code='inactive',
            )

class ApuestaForm(forms.ModelForm):
	class Meta:
		model = Apuesta
		fields = ['nota', 'tokens']

class NotaForm(forms.ModelForm):
	class Meta:
		model = Nota
		fields = '__all__'
	def clean(self):
		cleaned_data = self.cleaned_data
		alumno_lista = Alumno.objects.filter(equipo = cleaned_data['alumno'].equipo)

		nota_lista = Nota.objects.filter(Q(alumno__in=alumno_lista), Q(reto=cleaned_data['reto']))

		if nota_lista.count() > 0:
			raise ValidationError('Ya hay alguien de este equipo que ha respondido')

		return cleaned_data