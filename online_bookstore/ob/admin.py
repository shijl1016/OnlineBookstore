from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.ObUser)
admin.site.register(models.ObBook)
admin.site.register(models.ObRecord)