from django.shortcuts import render, redirect, get_object_or_404
from main.models import *
from datetime import date
from main.forms import *
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.views.generic import View, UpdateView, DetailView, CreateView, ListView
from django.http import HttpResponse
import json


def index(request):
    equipo_list = Equipo.objects.all()
    jugador_list = Profile.objects.filter(es_jugador=True)
    siguiente_meta = Meta.objects.filter(fecha__gte=date.today()).first()
    context = {
        'equipo_list': equipo_list,
        'jugador_list': jugador_list,
        'siguiente_meta': siguiente_meta,
    }

    return render(request, 'index.html', context)

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
    user_profile = request.user.perfil
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']

            #guardar avatar
            if 'foto' in request.FILES:
                user.perfil.foto = request.FILES['foto']

            #guardar portada
            if 'portada' in request.FILES:
                user.perfil.portada = request.FILES['portada']
            user.save()
            user.perfil.save()
        return redirect('profile_detail', id_profile=user_profile.id)
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'foto': request.user.perfil.foto,
            'public': request.user.perfil.public
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


class AlumnoDetailView(DetailView):
    model = Alumno
    template_name = 'alumno/detail.html'

    def get_context_data(self, **kwargs):
        context = super(AlumnoDetailView, self).get_context_data(**kwargs)
        context['form_mensaje'] = PostMensajeForm(initial={'alumno': self.object})
        return context


class MensajeCreateView(CreateView):
    model = Mensaje
    form_class = PostMensajeForm

    def form_valid(self, form):
        form.instance.escrito_por = self.request.user.perfil
        form.instance.para = Alumno.objects.get(id=self.kwargs['pk'])
        return super(MensajeCreateView, self).form_valid(form)


class PostAlumnoList(ListView):
    model = PostAlumno
    template_name = 'user/inbox.html'

    def get_queryset(self):
        return PostAlumno.objects.filter(escrito_por=self.request.user.perfil)


class PostAlumnoDetail(DetailView):
    model = PostAlumno
    template_name = 'user/mensaje.html'

    def get_context_data(self, **kwargs):
        context = super(PostAlumnoDetail, self).get_context_data(**kwargs)
        self.object.visto = True
        self.object.save()
        return context


class EquipoListView(ListView):
    model = Equipo
    template_name = 'equipo/list.html'


class EquipoDetailView(DetailView):
    model = Equipo
    template_name = 'equipo/detail.html'


class RetoListView(ListView):
    model = Reto
    template_name = 'reto/list.html'


class RetoDetailView(DetailView):
    model = Reto
    template_name = 'reto/detail.html'

    def get_context_data(self, **kwargs):
        context = super(RetoDetailView, self).get_context_data(**kwargs)
        context['apuesta_form'] = ApuestaForm(max_tokens=self.request.user.perfil.tokens_activos())
        context['apuesta_list'] = self.request.user.perfil.apuestas.filter(nota__reto=self.object)
        return context


class StoreView(ListView):
    model = Paquete
    template_name = 'store/store.html'

    def get_context_data(self, **kwargs):
        context = super(StoreView, self).get_context_data(**kwargs)
        context['pago_form'] = PagoForm()
        return context


class CompraCreateView(CreateView):
    model = Compra
    form_class = PagoForm

    def form_valid(self, form):
        form.instance.profile = self.request.user.perfil
        return super(CompraCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('store')


class ApuestaCreateView(CreateView):
    model = Apuesta
    form_class = ApuestaForm

    def form_valid(self, form):
        form.instance.user = self.request.user.perfil
        form.instance.nota = Nota.objects.get(id=self.kwargs['nota_id'])
        return super(ApuestaCreateView, self).form_valid(form)

    def get_success_url(self):
        return self.object.nota.reto.get_absolute_url()


class PerfilDetailView(DetailView):
    model = Profile
    template_name = 'user/detail.html'
