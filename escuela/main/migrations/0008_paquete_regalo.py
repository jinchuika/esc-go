# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-26 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20160823_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='paquete',
            name='regalo',
            field=models.BooleanField(default=False),
        ),
    ]
