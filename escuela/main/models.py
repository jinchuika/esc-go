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

	def puntos(self):
		puntos = 0
		apuestas = Apuesta.objects.filter(user=self)
		for a in apuestas:
			puntos = puntos + a.get_punteo('int')
		return puntos
	puntos = property(puntos)

	def __str__(self):
		return self.user.first_name + " " + self.user.last_name

class Paquete(models.Model):
	nombre = models.CharField(max_length=100)
	precio = models.DecimalField(max_digits=7, decimal_places=2)
	tokens = models.IntegerField()
	disponible = models.BooleanField(default=False)
	regalo = models.BooleanField(default=False)

	def __str__(self):
		return self.nombre

class Compra(models.Model):
	profile = models.ForeignKey('Profile')
	paquete = models.ForeignKey('Paquete')
	fecha = models.DateField(default=timezone.now)

	def __str__(self):
		return str(self.paquete) + " de " + str(self.profile)

def get_image_path(instance, filename):
	return os.path.join('photos', str(instance.id), filename)

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

	def promedio(self):
		total = 0
		alumno_lista = Alumno.objects.filter(equipo=self)
		for a in alumno_lista:
			total = total + a.promedio()
		return total/alumno_lista.count() if alumno_lista.count() > 0 else 0
	promedio = property(promedio)

	def blog(self):
		alumno_lista = Alumno.objects.filter(equipo=self)
		post_lista = PostAlumno.objects.filter(alumno__in=alumno_lista)
		return post_lista

	def __str__(self):
		return self.nombre

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

	def promedio(self):
		nota_list = Nota.objects.filter(alumno=self)
		total = 0
		for n in nota_list:
			total = total + n.nota
		return total/nota_list.count() if nota_list.count() > 0 else 0

	def __str__(self):
		return (self.nombre) + " " + self.apellido + " (" +str(self.equipo)+ ")"

class Materia(models.Model):
	nombre = models.CharField(max_length=100)

	def __str__(self):
		return self.nombre

class Reto(models.Model):
	materia = models.ForeignKey('Materia')
	fecha = models.DateField(unique=True)
	pt_1 = models.IntegerField()
	pt_2 = models.IntegerField()
	pt_3 = models.IntegerField()

	def ultimo_reto(fecha=date.today()):
		ultimo_reto = Reto.objects.filter(fecha__lt=fecha).order_by('fecha').reverse()
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

	def notas(self):
		nota_list = Nota.objects.filter(reto=self)
		return nota_list

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