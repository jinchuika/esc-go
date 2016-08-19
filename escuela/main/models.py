from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	tokens = models.IntegerField()

	def __str__(self):
		return self.user.first_name + " " + self.user.last_name

class Paquete(models.Model):
	nombre = models.CharField(max_length=100)
	precio = models.DecimalField(max_digits=7, decimal_places=2)
	tokens = models.IntegerField()

	def __str__(self):
		return self.nombre

class Compra(models.Model):
	profile = models.ForeignKey('Profile')
	paquete = models.ForeignKey('Paquete')

	def __str__(self):
		return str(self.paquete) + " de " + str(self.profile)

class Equipo(models.Model):
	nombre = models.CharField(max_length=100)

	def __str__(self):
		return self.nombre

class Alumno(models.Model):
	nombre = models.CharField(max_length=150, default='')
	apellido = models.CharField(max_length=150, default='')
	equipo = models.ForeignKey('Equipo')

	def __str__(self):
		return (self.nombre) + " " + self.apellido

class Materia(models.Model):
	nombre = models.CharField(max_length=100)

	def __str__(self):
		return self.nombre

class Reto(models.Model):
	materia = models.ForeignKey('Materia')
	fecha = models.DateField()
	pt_1 = models.IntegerField()
	pt_2 = models.IntegerField()
	pt_3 = models.IntegerField()

	def __str__(self):
		return str(self.materia) + " en " + str(self.fecha)



class LugarManager(models.Manager):
	def get_query_set(self, reto, alumno):
		return super(LugarManager, self).get_query_set().filter(Q(reto=self.reto), ~Q(alumno=self.alumno))
		

class Nota(models.Model):
	alumno = models.ForeignKey('Alumno')
	reto = models.ForeignKey('Reto')
	nota = models.IntegerField()

	objects = models.Manager()
	nota_reto = LugarManager()

	def lugar(self):
		lugar = 1
		list_nota = Nota.objects.filter(reto=self.reto)
		for i in list_nota:
			if self.nota < i.nota:
				lugar = lugar + 1
		return lugar

	def __str__(self):
		return str(self.alumno) + " " + str(self.nota) + " para " + str(self.reto)

class Apuesta(models.Model):
	user = models.ForeignKey('Profile')
	nota = models.ForeignKey('Nota')
	tokens = models.IntegerField()
	fecha = models.DateField()

	def punteo(self):
		lugar = self.nota.lugar()
		if lugar == 1:
			return self.tokens * self.nota.reto.pt_1
		if lugar == 2:
			return self.tokens * self.nota.reto.pt_2
		if lugar == 3:
			return self.tokens * self.nota.reto.pt_3
		return 0

	def __str__(self):
		return str(self.user) + " para " + str(self.nota)

