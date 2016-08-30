from django.shortcuts import render, redirect, get_object_or_404
from main.models import *
from datetime import timedelta, date, time
from main.forms import *
from django.forms import formset_factory, modelformset_factory
from django.contrib.auth import authenticate, login, views as auth_views, update_session_auth_hash
from django.views.generic import View, UpdateView
from django.http import HttpResponse
import json

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

def alumno_detail(request, id_alumno):
	alumno = get_object_or_404(Alumno, id=id_alumno)
	context = {
		'alumno': alumno
	}
	return render(request, 'alumno/detail.html', context)

def post_add(request, id_alumno):
	alumno = get_object_or_404(Alumno, id=id_alumno)
	form_post = PostAlumnoForm(request.POST or None)
	if form_post.is_valid():
		instance = form_post.save(commit=False)
		instance.alumno = Alumno.objects.get(id=id_alumno)
		instance.escrito_por = Profile.objects.get(user = request.user)
		instance.save()
		return redirect('equipo_blog', id_equipo=alumno.equipo.id)
	context = {
		'form_post': form_post,
		'alumno': alumno,
	}
	return render(request, 'alumno/add_post.html', context)

def mensaje_add(request, id_alumno):
	alumno = get_object_or_404(Alumno, id=id_alumno)
	form_mensaje = PostMensajeForm(request.POST or None)
	if form_mensaje.is_valid():
		instance = form_mensaje.save(commit=False)
		instance.alumno = alumno
		instance.escrito_por = Profile.objects.get(user = request.user)
		if instance.validar_regalo():
			compra = Compra(
				profile=instance.escrito_por, 
				paquete=Paquete.objects.filter(regalo=True,disponible=False).first()
				)
			compra.save()
		instance.save()
		return redirect('equipo_blog', id_equipo=alumno.equipo.id)
	context = {
		'form_mensaje': form_mensaje,
		'alumno': alumno,
	}
	return render(request, 'alumno/add_mensaje.html', context)

def equipo_detail(request, id_equipo):
	equipo = get_object_or_404(Equipo, id=id_equipo)
	alumno_list = Alumno.objects.filter(equipo=equipo)
	blog = equipo.blog()
	context = {
		'equipo': equipo,
		'alumno_list': alumno_list,
		'blog': blog
	}
	return render(request, 'equipo/detail.html', context)

def equipo_blog(request, id_equipo):
	equipo = get_object_or_404(Equipo, id=id_equipo)
	alumno_lista = Alumno.objects.filter(equipo=equipo)
	post_lista = PostAlumno.objects.filter(alumno__in=alumno_lista)
	context = {
		'equipo': equipo,
		'alumno_lista': alumno_lista,
		'post_lista': post_lista,
	}
	return render(request, 'equipo/blog.html', context)

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

			if form_apuesta.is_valid():
				apuesta = form_apuesta.save(commit=False)
				if apuesta.tokens <= profile.first().tokens_activos():
					apuesta.user = profile.first()
					apuesta.save()
		return redirect('reto_detail', id_reto=id_reto)
	#al entrar a la vista
	else:
		context = {}
		if request.user.is_authenticated():
			profile = Profile.objects.filter(user=request.user)
			apuesta_list = Apuesta.objects.filter(nota__in=nota_list, user=profile)
			context['apuesta_list'] = apuesta_list
			tokens_activos = 0 if profile.count() == 0 else profile.first().tokens_activos()
			form_apuesta = ApuestaForm(nota_list=nota_list, tokens_activos=tokens_activos)
			context['form_apuesta'] = form_apuesta
		context['reto'] = reto
		context['nota_list'] = nota_list
		return render(request, 'reto/detail.html', context)

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
	paquete_lista = []
	for paquete in Paquete.objects.filter(disponible=True):
		paquete_lista.append({
			'paquete': paquete,
			'form': CompraForm(initial={'paquete':paquete})
			})
	context = {
		'profile': profile,
		'paquete_lista': paquete_lista,
	}
	return render(request, 'store/index.html', context)

def crear_compra(request):
	if request.method=='POST':
		paquete = Paquete.objects.get(id=request.POST.get('paquete_id'))
		user = User.objects.get(id=request.user.id)
		profile = Profile.objects.get(user=user)
		compra = Compra(paquete=paquete, profile=profile)
		compra.save()
		profile
		print(compra)
		return HttpResponse(
			json.dumps({
				'done': 1,
				'tokens': profile.tokens_activos()
				}),
			content_type="application/json"
			)


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

class UserUpdate(UpdateView):
	model = Profile
	form_class = UserForm
	template_name = 'user/update.html'
	success_url = 'index'
	context_object_name = 'profile'

	def get_object(self, queryset=None):
		return self.request.user

	def form_valid(self, form):
		clean = form.cleaned_data
		context = {}
		self.object = context.save(clean)
		return super(UserUpdate, self).form_valid(form)

def profile_edit(request):
	user_profile = request.user.profile
	if request.method == 'POST':
		form = ProfileForm(request.POST)
		if form.is_valid():
			user = request.user
			user.first_name = form.cleaned_data['first_name']
			user.last_name = form.cleaned_data['last_name']
			user.email = form.cleaned_data['email']
			user.profile.public = form.cleaned_data['public']

			#guardar avatar
			if 'foto' in request.FILES:
				user.profile.foto = request.FILES['foto']

			user.save()
			user.profile.save()
		return redirect('profile_detail', id_profile=user_profile.id)
	else:
		initial = {
			'first_name': request.user.first_name,
			'last_name': request.user.last_name,
			'email': request.user.email,
			'foto': request.user.profile.foto,
			'public': request.user.profile.public
		}
		form = ProfileForm(initial=initial)
	return render(request, 'user/update.html', {'form': form})
		

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

def password_change(request):
	if request.method == 'POST':
		form = PasswordChangeForm(user=request.user, data=request.POST)
		if form.is_valid():
			form.save()
			update_session_auth_hash(request, form.user)
			return redirect('profile_detail', id_profile=request.user.profile.id)
	else:
		form = PasswordChangeForm(user=request.user)
	return render(request, 'user/password_change.html', {'form': form})