from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import timedelta, date, time
from django.utils import timezone

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	tokens = models.IntegerField(default=0)

	def tokens_activos(self, fecha=date.today()):
		tokens = 0
		ultimo_reto = Reto.ultimo_reto()
		compra_list = Compra.objects.filter(profile=self, fecha__range=(ultimo_reto.fecha, fecha))
		apuesta_list = Apuesta.objects.filter(user=self, fecha__range=(ultimo_reto.fecha, fecha))
		for c in compra_list:
			tokens = tokens + c.paquete.tokens
		for a in apuesta_list:
			tokens = tokens - a.tokens
		return tokens

	def puntos(self):
		puntos = 0
		apuestas = Apuesta.objects.filter(user=self)
		for a in apuestas:
			puntos = puntos + a.punteo()
		return puntos
	puntos = property(puntos)

	def __str__(self):
		return self.user.first_name + " " + self.user.last_name

class Paquete(models.Model):
	nombre = models.CharField(max_length=100)
	precio = models.DecimalField(max_digits=7, decimal_places=2)
	tokens = models.IntegerField()
	disponible = models.BooleanField(default=False)

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
	logo = models.ImageField(
		upload_to="main/images/equipo_logo",
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

	def __str__(self):
		return self.nombre

class Alumno(models.Model):
	nombre = models.CharField(max_length=150, default='')
	apellido = models.CharField(max_length=150, default='')
	equipo = models.ForeignKey('Equipo')

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
		return Reto.objects.filter(fecha__lt=fecha).order_by('fecha').reverse()[0]

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

	def puntos_token(self):
		if self.lugar() == 1:
			return self.reto.pt_1
		if self.lugar() == 2:
			return self.reto.pt_2
		if self.lugar() == 3:
			return self.reto.pt_3
		return 0

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

	def __str__(self):
		return str(self.user) + " para " + str(self.nota)

