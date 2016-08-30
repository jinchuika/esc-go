from django import forms
from django.forms import ModelForm, ModelChoiceField, formset_factory, modelformset_factory
from main.models import *
import datetime
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

class UserModelForm(ModelForm):
	class Meta:
		model = User
		fields = ['username', 'password', 'first_name', 'last_name']

class UserForm(forms.ModelForm):
	password = forms.CharField(widget=forms.PasswordInput)
	class Meta:
		model = User
		fields = ('username', 'password', 'email', 'first_name', 'last_name')

class ProfileModelForm(UserForm):
	class Meta:
		model = Profile
		exclude = ('password',)
		fields = ['foto']

class ProfileForm(forms.Form):
	first_name = forms.CharField(required=True)
	last_name = forms.CharField(required=True)
	email = forms.EmailField()
	foto = forms.ImageField(required=False)
	public = forms.BooleanField(required=False)

	def clean(self):
		cleaned_data = self.cleaned_data
		


class LoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("La cuenta está inactiva."),
                code='inactive',
            )

class ApuestaChoiceField(ModelChoiceField):
	def label_from_instance(self, obj):
		return str(obj.alumno)

class ApuestaForm(forms.ModelForm):
	nota = ApuestaChoiceField(queryset=Nota.objects.none(), label='Nota', empty_label=None)

	class Meta:
		model = Apuesta
		fields = ['nota', 'tokens']

	def __init__(self, *args, **kwargs):
		qs = kwargs.pop('nota_list')
		tokens_activos = kwargs.pop('tokens_activos')
		super(ApuestaForm, self).__init__(*args, **kwargs)
		self.fields['nota'].queryset = qs
		self.fields['tokens'] = forms.IntegerField(max_value=tokens_activos, min_value=0)

	def clean(self):
		cleaned_data = self.cleaned_data
		if int(cleaned_data['tokens']) <= 0:
			raise ValidationError('Debe apostar más de un token')

		return cleaned_data


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

class PostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = '__all__'

class PostAlumnoForm(PostForm):
	class Meta:
		model = PostAlumno
		fields = [
			'titulo',
			'cuerpo',
			'categoria'
		]

class PostMensajeForm(PostForm):
	class Meta:
		model = Mensaje
		fields = [
			'titulo',
			'cuerpo',
		]

class CompraForm(forms.ModelForm):
	tokens = ''
	paquete_data = Paquete()

	def __init__(self, *args, **kwargs):
		super(CompraForm, self).__init__(*args, **kwargs)
		self.paquete_data = self.fields['paquete'].initial

	class Meta:
		model = Compra
		fields = ['paquete']
		widgets = {
			'paquete': forms.HiddenInput
		}

CompraFormSet = formset_factory(CompraForm)