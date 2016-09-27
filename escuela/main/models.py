import os
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import timedelta, date, time
from django.utils import timezone
from easy_thumbnails.fields import ThumbnailerImageField

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	public = models.BooleanField(default=False)
	es_jugador = models.BooleanField(default=True)
	foto = ThumbnailerImageField(
		upload_to="perfil_usuario",
        null=True,
        blank=True,
        editable=True,
		)
	portada = ThumbnailerImageField(
		upload_to="portada_usuario",
        null=True,
        blank=True,
        editable=True,
        help_text="Portada de usuario",
        verbose_name="Portada de usuario"
		)

	def tokens_activos(self, fecha=date.today()):
		tokens = 0
		ultimo_reto = Reto.ultimo_reto()
		if ultimo_reto:
			compra_list = Compra.objects.filter(profile=self, fecha__range=(ultimo_reto.fecha, fecha))
			apuesta_list = Apuesta.objects.filter(user=self, fecha__range=(ultimo_reto.fecha, fecha))
		else:
			compra_list = Compra.objects.filter(profile=self, fecha__lte=fecha)
			apuesta_list = Apuesta.objects.filter(user=self, fecha__lte=fecha)
		for c in compra_list:
			tokens = tokens + c.paquete.tokens
		for a in apuesta_list:
			tokens = tokens - a.tokens
		return tokens

	def get_puntos(self, fecha=date.today()):
		puntos = 0
		apuestas = Apuesta.objects.filter(user=self, fecha__lt=fecha)
		for a in apuestas:
			puntos = puntos + a.get_punteo('int')
		return puntos
	puntos = property(get_puntos)


	def get_lugar(self, fecha=date.today()):
		profile_list = Profile.objects.all()
		lugar = profile_list.count() + 1
		for p in profile_list:
			if self.get_puntos(fecha) >= p.get_puntos(fecha):
				lugar = lugar - 1
		return lugar

	def __str__(self):
		return self.user.first_name + " " + self.user.last_name

class Paquete(models.Model):
	nombre = models.CharField(max_length=100)
	precio = models.DecimalField(max_digits=7, decimal_places=2)
	tokens = models.IntegerField()
	disponible = models.BooleanField(default=False)
	regalo = models.BooleanField(default=False)
	imagen = ThumbnailerImageField(
		upload_to="imagen_paquete",
        null=True,
        blank=True,
        editable=True,
        help_text="Imagen de paquete",
        verbose_name="Imagen de paquete"
		)

	def __str__(self):
		return self.nombre

class Compra(models.Model):
	profile = models.ForeignKey('Profile')
	paquete = models.ForeignKey('Paquete')
	fecha = models.DateField(default=timezone.now)

	def __str__(self):
		return str(self.paquete) + " de " + str(self.profile)

class Equipo(models.Model):
	nombre = models.CharField(max_length=100)
	logo = ThumbnailerImageField(
		upload_to="equipo_logo",
        null=True,
        blank=True,
        editable=True,
        help_text="Logo de equipo",
        verbose_name="Logo de equipo"
		)
	portada = ThumbnailerImageField(
		upload_to="equipo_portada",
        null=True,
        blank=True,
        editable=True,
        help_text="Portada de equipo",
        verbose_name="Portada de equipo"
		)
	descripcion = models.TextField(null=True)

	def get_promedio(self, fecha=date.today()):
		total = 0
		alumno_lista = Alumno.objects.filter(equipo=self)
		for a in alumno_lista:
			total = total + a.promedio(fecha)
		return total/alumno_lista.count() if alumno_lista.count() > 0 else 0
	promedio = property(get_promedio)

	def blog(self):
		alumno_lista = Alumno.objects.filter(equipo=self)
		post_lista_all = PostAlumno.objects.filter(alumno__in=alumno_lista).order_by('fecha')[:10]
		post_lista = reversed(post_lista_all)
		return post_lista

	def __str__(self):
		return self.nombre

class Grado(models.Model):
	numero = models.IntegerField()
	seccion = models.CharField(max_length=2, null=True, blank=True)

	def __str__(self):
		return str(self.numero) + " " + self.seccion

class Alumno(models.Model):
	nombre = models.CharField(max_length=150, default='')
	apellido = models.CharField(max_length=150, default='')
	equipo = models.ForeignKey('Equipo')
	foto = ThumbnailerImageField(
		upload_to="perfil_alumno",
        null=True,
        blank=True,
        editable=True,
		)
	grado = models.ForeignKey('Grado', null=True, blank=True)
	animal = models.CharField(max_length=50, null=True, blank=True)
	color = models.CharField(max_length=50, null=True, blank=True)
	sueno = models.CharField(max_length=70, null=True, blank=True)
	juego = models.CharField(max_length=70, null=True, blank=True)
	edad = models.IntegerField(null=True, blank=True)

	def promedio(self, fecha=date.today()):
		reto_list = Reto.objects.filter(fecha__lte=fecha)
		nota_list = Nota.objects.filter(alumno=self, reto__in=reto_list)
		total = 0
		for n in nota_list:
			total = total + n.nota
		return total/nota_list.count() if nota_list.count() > 0 else 0

	def blog(self):
		post_lista_all = PostAlumno.objects.filter(alumno=self).order_by('fecha')[:10]
		post_lista = reversed(post_lista_all)
		return post_lista


	def __str__(self):
		return (self.nombre) + " " + self.apellido + " (" +str(self.equipo)+ ")"

class Materia(models.Model):
	nombre = models.CharField(max_length=100)
	bg = ThumbnailerImageField(
		upload_to="materia_media",
        null=True,
        blank=True,
        editable=True,
		)
	icon = ThumbnailerImageField(
		upload_to="materia_media",
        null=True,
        blank=True,
        editable=True,
		)

	def __str__(self):
		return self.nombre

class Reto(models.Model):
	materia = models.ForeignKey('Materia')
	fecha = models.DateField(unique=True)
	pt_1 = models.IntegerField()
	pt_2 = models.IntegerField()
	pt_3 = models.IntegerField()

	def ultimo_reto(fecha=date.today()):
		ultimo_reto = Reto.objects.filter(fecha__lte=fecha).order_by('fecha').reverse()
		if ultimo_reto.count() < 1:
			return None
		else:
			return ultimo_reto[0]

	def proximo_reto(fecha=date.today()):
		proximo_reto = Reto.objects.filter(fecha__gt=fecha).order_by('fecha')
		if proximo_reto.count() < 1:
			return None
		else:
			return proximo_reto[0]

	def anterior(self):
		anterior = Reto.objects.filter(fecha__lte=self.fecha).order_by('fecha')
		if anterior.count() < 1:
			return None
		else:
			return anterior[0]
	
	def siguiente(self):
		siguiente = Reto.objects.filter(fecha__gt=self.fecha).order_by('fecha')
		if siguiente.count() < 1:
			return None
		else:
			return siguiente[0]

	def notas(self):
		nota_list = Nota.objects.filter(reto=self)
		return nota_list

	def puntos_profile(self, user):
		puntos = 0
		nota_list = Nota.objects.filter(reto=self)
		for apuesta in Apuesta.objects.filter(user=user, nota__in=nota_list):
		 	if id_number(apuesta.get_punteo()):
		 		puntos = puntos + apuesta.get_punteo()
		return puntos


	def __str__(self):
		return str(self.materia) + " en " + str(self.fecha)

class Nota(models.Model):
	alumno = models.ForeignKey('Alumno')
	reto = models.ForeignKey('Reto')
	nota = models.IntegerField()

	objects = models.Manager()

	class Meta:
		unique_together = ('alumno', 'reto')

	def lugar(self):
		lugar = 1
		list_nota = Nota.objects.filter(reto=self.reto)
		for i in list_nota:
			if self.nota < i.nota:
				lugar = lugar + 1
		return lugar

	def get_nota(self):
		if self.reto.fecha <= date.today():
			return self.nota
		else:
			return '?'

	def get_lugar(self):
		if self.reto.fecha <= date.today():
			return self.lugar()
		else:
			return '?'

	def puntos_token(self):
		if self.lugar() == 1:
			return self.reto.pt_1
		if self.lugar() == 2:
			return self.reto.pt_2
		if self.lugar() == 3:
			return self.reto.pt_3
		return 0

	def __unicode__(self):
		return u'{0}'.format(self.nota)

	def __str__(self):
		return str(self.alumno) + " " + str(self.nota) + " para " + str(self.reto)

class Apuesta(models.Model):
	user = models.ForeignKey('Profile')
	nota = models.ForeignKey('Nota')
	tokens = models.IntegerField()
	fecha = models.DateField(default=timezone.now)

	def punteo(self):
		lugar = self.nota.lugar()
		return self.tokens * self.nota.puntos_token()

	def get_punteo(self, tipo='string'):
		if self.nota.reto.fecha <= date.today():
			return self.punteo()
		else:
			return '?' if tipo=='string' else 0

	def __str__(self):
		return str(self.user) + " para " + str(self.nota)

class PostCategoria(models.Model):
	nombre = models.CharField(max_length=250)

	def __str__(self):
		return self.nombre

class Post(models.Model):
	titulo = models.CharField(max_length=150)
	fecha = models.DateField(default=timezone.now)
	cuerpo = models.TextField()
	escrito_por = models.ForeignKey('Profile')

	def __str__(self):
		return self.titulo

class PostAlumno(Post):
	alumno = models.ForeignKey('Alumno')
	categoria = models.ForeignKey('PostCategoria', null=True, blank=True)

class Mensaje(Post):
	cobrado = models.BooleanField(default=True)

	def validar_regalo(self):
		mensajes_actuales = Mensaje.objects.filter(escrito_por=self.escrito_por, fecha__range=(Reto.ultimo_reto().fecha, Reto.proximo_reto().fecha)) 
		if mensajes_actuales.count() < 1:
			return True
		else:
			return False

class Meta(models.Model):
	cantidad = models.DecimalField(max_digits=8, decimal_places=2)
	fecha = models.DateField()
	descripcion = models.CharField(max_length=60)

	def __str__(self):
		return self.descripcion

	def get_progreso(self):
		compra_list = Compra.objects.filter(fecha__lte=self.fecha)
		total = 0
		for c in compra_list:
			total += c.paquete.precio
		porcentaje = total / self.cantidad * 100
		return {'total': total, 'porcentaje' : porcentaje}
	progreso = property(get_progreso)