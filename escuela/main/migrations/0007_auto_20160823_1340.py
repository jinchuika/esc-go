# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-23 13:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20160822_1331'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=150)),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('cuerpo', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='PostCategoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=250)),
            ],
        ),
        migrations.RemoveField(
            model_name='profile',
            name='tokens',
        ),
        migrations.AddField(
            model_name='alumno',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='perfil_alumno'),
        ),
        migrations.AddField(
            model_name='profile',
            name='es_jugador',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='perfil_usuario'),
        ),
        migrations.AddField(
            model_name='profile',
            name='public',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='logo',
            field=models.ImageField(blank=True, help_text='Logo de equipo', null=True, upload_to='equipo_logo', verbose_name='Logo de equipo'),
        ),
        migrations.CreateModel(
            name='Mensaje',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.Post')),
                ('cobrado', models.BooleanField(default=True)),
            ],
            bases=('main.post',),
        ),
        migrations.CreateModel(
            name='PostAlumno',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.Post')),
                ('alumno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Alumno')),
                ('categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.PostCategoria')),
            ],
            bases=('main.post',),
        ),
        migrations.AddField(
            model_name='post',
            name='escrito_por',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.Profile'),
        ),
    ]
