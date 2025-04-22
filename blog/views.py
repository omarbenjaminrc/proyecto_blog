from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Articulo

class VistaListaArticulos(ListView):
    '''
    Vista para listar los articulos publicados.
    '''

    model = Articulo
    template_name = 'blog/lista_articulos.html'
    context_object_name = 'articulos'
    ordering = ['-fecha_creacion']

class VistaDetalleArticulo(DetailView):
    '''
    Vista para mostras detalles de articulos especificos
    '''
    model = Articulo
    template_name = 'blog/detalle_articulo.html' 
    context_object_name = 'articulo'

    #estos parametros de dicen a django que no busque por id sino por slug
    slug_field = 'slug'
    slug_url_kwarg = 'slug'