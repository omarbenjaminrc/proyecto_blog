from django.contrib import admin
from .models import Articulo, Categoria

class ArticuloAdmin(admin.ModelAdmin):
    model = Articulo
    list_display = ['titulo', 'fecha_creacion', 'fecha_actualizacion', 'mostrar_categorias']
    search_fields = ['titulo']
    filter_horizontal = ('categorias',)

    def mostrar_categorias(self, obj):
        return ", ".join([c.nombre for c in obj.categorias.all()])
    mostrar_categorias.short_description = 'Categorías'

admin.site.register(Articulo, ArticuloAdmin)
admin.site.register(Categoria)