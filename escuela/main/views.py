from django.shortcuts import render, redirect, get_object_or_404
from main.models import *
from datetime import timedelta, date, time
from main.forms import *
from django.forms import formset_factory, modelformset_factory
from django.contrib.auth import authenticate, login
from django.views.generic import View

def index(request):
	equipo_list = Equipo.objects.all()
	profile_list = Profile.objects.all()
	reto = Reto.objects.filter(fecha__gt=date.today()).first()
	sorted(profile_list, key=lambda p: p.puntos)
	context = {
		'equipo_list': equipo_list,
		'profile_list': profile_list,
		'reto': reto
	}

	return render(request, 'index.html', context)

def equipo_detail(request, id_equipo):
	equipo = get_object_or_404(Equipo, id=id_equipo)
	alumno_list = Alumno.objects.filter(equipo=equipo)
	context = {
		'equipo': equipo,
		'alumno_list': alumno_list,
	}
	return render(request, 'equipo/detail.html', context)

def reto_detail(request, id_reto):
	reto = get_object_or_404(Reto, id=id_reto)
	nota_list = Nota.objects.filter(reto=reto)
	apuesta_list = Apuesta.objects.filter(nota__in=nota_list)
	context = {
		'reto': reto,
		'apuesta_list': apuesta_list,
		'nota_list': nota_list
	}
	return render(request, 'reto/detail.html', context)

def profile_add(request):
	if request.method=='POST':
		profile_form = ProfileModelForm(request.POST)
		if profile_form.is_valid():
			profile = profile_form.save(commit=False)
			profile.save()
			return redirect('profile_detail', id_profile=profile.id)
	else:
		user = User()
		ProfileFormset = modelformset_factory(ProfileModelForm, fields=('username', 'password', 'first_name', 'last_name'))
		profile_form = ProfileFormset(instance=user)
	return render(request, 'user/add.html', {'profile_form': profile_form})

class UserFormView(View):
	form_class = UserForm
	template_name = 'user/add.html'

	#formulario en blanco
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	#nuevo registro
	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():
			user = form.save(commit=False)
			username = form.cleaned_data['username']
			email = form.cleaned_data['email']
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			password = form.cleaned_data['password']
			
			user.set_password(password)
			user.save()

			profile = Profile(user=user)
			profile.save()

			user = authenticate(username = username, password=password)

			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect('index')

		return render(request, self.template_name, {'form': form})

class UserLoginView(View):
	form_class = LoginForm
	template_name = 'user/login.html'

	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	#nuevo registro
	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():
			user = form.save(commit=False)
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']

			user = authenticate(username = username, password=password)

			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect('index')

		return render(request, self.template_name, {'form': form})