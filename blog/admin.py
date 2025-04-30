from django.contrib import admin
from .models import Articulo

class ArticuloAdmin(admin.ModelAdmin):
    model = Articulo
    list_display = ['titulo', 'fecha_creacion', 'fecha_actualizacion']
    search_fields = ['titulo']

admin.site.register(Articulo, ArticuloAdmin)