# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-31 17:56
from __future__ import unicode_literals

from django.db import migrations
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_paquete_regalo'),
    ]

    operations = [
        migrations.AddField(
            model_name='materia',
            name='bg',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='perfil_usuario'),
        ),
        migrations.AddField(
            model_name='materia',
            name='icon',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='perfil_usuario'),
        ),
        migrations.AlterField(
            model_name='alumno',
            name='foto',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='perfil_alumno'),
        ),
        migrations.AlterField(
            model_name='equipo',
            name='logo',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, help_text='Logo de equipo', null=True, upload_to='equipo_logo', verbose_name='Logo de equipo'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='foto',
            field=easy_thumbnails.fields.ThumbnailerImageField(blank=True, null=True, upload_to='perfil_usuario'),
        ),
    ]
