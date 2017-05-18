import simplejson
import paypalrestsdk
from datetime import datetime
from django import forms
from django.forms import ModelForm, ModelChoiceField, formset_factory
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .payment_template import form_parametros
from main.models import *


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


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=True, label='Nombre')
    last_name = forms.CharField(required=True, label='Apellido')
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ('foto',)


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Name',
            'class': 'input-calss_name'})

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("La cuenta está inactiva."),
                code='inactive',
            )


class ApuestaChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return str(obj.alumno.equipo)


class ApuestaForm(forms.ModelForm):
    class Meta:
        model = Apuesta
        fields = ('tokens',)

    def __init__(self, *args, **kwargs):
        max_tokens = kwargs.pop('max_tokens', False)
        super(ApuestaForm, self).__init__(*args, **kwargs)
        if max_tokens:
            self.fields['tokens'].widget = forms.NumberInput(attrs={'min': 1, 'max': max_tokens})
        else:
            self.fields['tokens'].widget = forms.NumberInput(attrs={'min': 1,  'max': 0})

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
        alumno_lista = Alumno.objects.filter(equipo=cleaned_data['alumno'].equipo)

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
            'imagen'
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


class PagoForm(forms.ModelForm):
    first_name = forms.CharField(
        label='Nombre',
        required=True,
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'Nombre'}))
    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': 'Apellido'}))
    card_type = forms.ModelChoiceField(
        required=True,
        label='Tipo de tarjeta',
        queryset=TipoTarjeta.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Tipo de tarjeta'}))
    number = forms.CharField(
        max_length=20,
        label='Card number',
        widget=forms.TextInput(attrs={'class': 'form-control ', 'placeholder': '0000 0000 0000 0000'}))
    expire_month = forms.IntegerField(
        help_text='2 digits',
        label='Month',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-white',
            'min': '1',
            'max': '12',
            'placeholder': 'MM'}))
    expire_year = forms.IntegerField(
        help_text='4 digits',
        label='Year',
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-white',
            'min': datetime.now().year,
            'placeholder': 'YYYY',
            'size': 4, 'maxlength': 4}))
    cvv2 = forms.CharField(
        label='CVV',
        max_length=4, widget=forms.NumberInput(attrs={
            'class': 'form-control form-white',
            'min': '1',
            'placeholder': 'CVV'}))

    class Meta:
        model = Compra
        fields = ('paquete', 'payment_ref')
        widgets = {
            'paquete': forms.HiddenInput(),
            'payment_ref': forms.HiddenInput()
        }

    def clean(self):
        cleaned_data = super(PagoForm, self).clean()
        paypalrestsdk.configure({
            "mode": settings.PP_MODE,
            "client_id": settings.PP_CLIENT_ID,
            "client_secret": settings.PP_CLIENT_SECRET})
        credit_card = {
            "type": cleaned_data.get("card_type").tipo_tarjeta,
            "number": cleaned_data.get("number"),
            "expire_month": cleaned_data.get("expire_month"),
            "expire_year": cleaned_data.get("expire_year"),
            "cvv2": cleaned_data.get("cvv2"),
            "first_name": cleaned_data.get("first_name"),
            "last_name": cleaned_data.get("last_name")}
        payment = paypalrestsdk.Payment(
            form_parametros(credit_card,
                simplejson.dumps(cleaned_data.get("paquete").precio),
                "Paquete de tokens " + cleaned_data.get("paquete").nombre))
        if payment.create():
            # send_thanks_email(cleaned_data.get("first_name"), cleaned_data.get("last_name"), cleaned_data.get("mail"), cleaned_data.get("total"))
            print("Payment[%s] created successfully" % (payment.id))
        else:
            err_text = ""
            if "details" in payment.error:
                err_text = "Error given was: "
                for err in payment.error['details']:
                    err_text += err['issue'] + " "
            raise forms.ValidationError("Error during payment due to invalid credit card. Please check your credentials." + err_text)
        print(cleaned_data)
