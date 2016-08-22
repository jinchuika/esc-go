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
	reto_lista = Reto.objects.filter(fecha__lt=date.today()).order_by('fecha')
	siguiente_reto = Reto.objects.filter(fecha__gt=date.today()).order_by('fecha').first()
	sorted(profile_list, key=lambda p: p.puntos)
	context = {
		'equipo_list': equipo_list,
		'profile_list': profile_list,
		'reto_lista': reto_lista,
		'siguiente_reto': siguiente_reto,
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
	tokens_activos = 0
	#Al crear un nuevo registro
	if request.method=='POST':
		if request.user.is_authenticated():
			profile = Profile.objects.filter(user=request.user)
			tokens_activos = 0 if profile.count() == 0 else profile.first().tokens_activos()
			form_apuesta = ApuestaForm(request.POST, nota_list=nota_list, tokens_activos=tokens_activos)
			
			apuesta = form_apuesta.save(commit=False)
			if form_apuesta.is_valid():
				apuesta = form_apuesta.save(commit=False)
				if apuesta.tokens <= profile.first().tokens_activos():
					apuesta.user = profile.first()
					apuesta.save()
		return redirect('reto_detail', id_reto=id_reto)
	#al entrar a la vista
	else:
		if request.user.is_authenticated():
			profile = Profile.objects.filter(user=request.user)
			apuesta_list = Apuesta.objects.filter(nota__in=nota_list, user=profile)
			tokens_activos = 0 if profile.count() == 0 else profile.first().tokens_activos()
			form_apuesta = ApuestaForm(nota_list=nota_list, tokens_activos=tokens_activos)
		context = {
			'reto': reto,
			'apuesta_list': apuesta_list,
			'nota_list': nota_list,
			'form_apuesta': form_apuesta,
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

def profile_detail(request, id_profile):
	profile = get_object_or_404(Profile, id=id_profile)
	compra_list = Compra.objects.filter(profile=profile)
	apuesta_list = Apuesta.objects.filter(user=profile)
	context = {
		'profile': profile,
		'compra_list': compra_list,
		'apuesta_list': apuesta_list,
	}
	return render(request, 'user/detail.html', context)

def tienda(request):
	user = User.objects.get(id=request.user.id)
	profile = Profile.objects.get(user=user)
	paquete_lista = Paquete.objects.filter(disponible=True)
	context = {
		'profile': profile,
		'paquete_lista': paquete_lista
	}
	return render(request, 'store/index.html', context)

def compra_add(request, id_paquete):
	user = User.objects.get(id=request.user.id)
	profile = Profile.objects.get(user=user)
	paquete = Paquete.objects.get(id=id_paquete)
	compra = Compra(paquete=paquete, profile=profile)
	compra.save()
	return redirect('profile_detail', id_profile=profile.id)

class NotaFormView(View):
	form_class = NotaForm
	template_name = 'n/add.html'

	#formulario en blanco
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		form = self.form_class(request.POST)

		if form.is_valid():
			nota = form.save(commit=False)
			nota.save()
			return redirect('nota_add')
		return render(request, self.template_name, {'form': form})

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