# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-16 14:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20170216_1356'),
    ]

    operations = [
        migrations.AddField(
            model_name='mensaje',
            name='para',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.Alumno'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='perfil', to=settings.AUTH_USER_MODEL),
        ),
    ]
