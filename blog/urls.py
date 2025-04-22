from django.urls import path
from .views import VistaDetalleArticulo, VistaListaArticulos

app_name = 'blog'

urlpatterns = [
    path('', VistaListaArticulos.as_view(), name= 'lista_articulos'),
    path('articulo/<slug:slug>', VistaDetalleArticulo.as_view(), name= 'detalle_articulo')
]