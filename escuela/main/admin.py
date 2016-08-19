from django.contrib import admin
from main.models import *
from django.apps import apps
# Register your models here.
for model in apps.get_app_config('main').models.values():
    admin.site.register(model)