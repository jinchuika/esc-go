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
	siguiente_meta = Meta.objects.filter(fecha__gte=date.today()).first()
	context = {
		'equipo_list': equipo_list,
		'profile_list': profile_list,
		'reto_lista': reto_lista,
		'siguiente_reto': siguiente_reto,
		'siguiente_meta': siguiente_meta,
	}

	return render(request, 'index.html', context)

def alumno_detail(request, id_alumno):
	context = {}
	alumno = get_object_or_404(Alumno, id=id_alumno)
	if request.user.is_authenticated():
		if request.method=='POST':
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
				return redirect('alumno_detail', id_alumno=alumno.id)
		else:
			form_mensaje = PostMensajeForm()
		context['form_mensaje'] = form_mensaje

	context['alumno'] = alumno
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
		return redirect('alumno_detail', id_equipo=alumno.equipo.id)
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
	post_lista_all = PostAlumno.objects.filter(alumno__in=alumno_lista).order_by('fecha')[:10]
	post_lista = reversed(post_lista_all)
	context = {
		'equipo': equipo,
		'alumno_lista': alumno_lista,
		'post_lista': post_lista,
	}
	return render(request, 'equipo/blog.html', context)

def reto_all(request):
	reto_list = []
	for reto in Reto.objects.all().order_by('fecha'):
		nota_list_all = Nota.objects.filter(reto=reto).order_by('nota')
		nota_list = nota_list_all
		ganador = nota_list_all.last().alumno if reto.fecha <= date.today() else None
		pasado = True if reto.fecha <= date.today() else False
		reto_list.append({
			'reto': reto,
			'nota_list': nota_list,
			'ganador': ganador,
			'pasado': pasado
			})
	context = {'reto_list': reto_list}
	return render(request, 'reto/all.html', context)

def reto_detail(request, id_reto):
	reto = get_object_or_404(Reto, id=id_reto)
	nota_list = Nota.objects.filter(reto=reto)
	tokens_activos = 0
	#Al crear un nuevo registro
	if request.method=='POST':
		if request.user.is_authenticated():
			profile = request.user.profile
			tokens_activos = profile.tokens_activos()
			form_apuesta = ApuestaForm(request.POST, nota_list=nota_list, tokens_activos=tokens_activos)

			if form_apuesta.is_valid() and form_apuesta.cleaned_data['tokens']>0:
				apuesta = form_apuesta.save(commit=False)
				if apuesta.tokens <= profile.tokens_activos():
					apuesta.user = profile
					apuesta.save()
		return redirect('reto_detail', id_reto=id_reto)
	#al entrar a la vista
	else:
		context = {}
		context['retos_anteriores'] = Reto.objects.filter(fecha__lte=date.today())

		if request.user.is_authenticated():
			profile = Profile.objects.filter(user=request.user)
			apuesta_list = Apuesta.objects.filter(nota__in=nota_list, user=profile)
			context['apuesta_list'] = apuesta_list
			
			tokens_activos = 0 if profile.count() == 0 else profile.first().tokens_activos()
			
			#formulario para postar si el reto sigue vigente
			if reto.fecha > date.today() and reto == Reto.proximo_reto():
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

def profile_detail_chart(request, id_profile):
	reto_list = {}
	reto_list['materia'] = []
	reto_list['fecha'] = []
	reto_list['lugar'] = []
	reto_list['puntos'] = []
	profile = Profile.objects.get(id=id_profile)
	for reto in Reto.objects.filter(fecha__lte=date.today()).order_by('fecha'):
		reto_list['materia'].append(str(reto.materia))
		reto_list['fecha'].append(str(reto.fecha))
		reto_list['lugar'].append(profile.get_lugar(reto.fecha))
		reto_list['puntos'].append(profile.get_puntos(reto.fecha))
	return HttpResponse(
		json.dumps(reto_list),
		content_type="application/json"
		)
		

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

			#guardar avatar
			if 'foto' in request.FILES:
				user.profile.foto = request.FILES['foto']

			#guardar portada
			if 'portada' in request.FILES:
				user.profile.portada = request.FILES['portada']
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