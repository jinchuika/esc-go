# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-19 20:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20160819_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='compra',
            name='fecha',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
