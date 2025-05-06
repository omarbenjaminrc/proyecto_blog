from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Articulo, Categoria

class VistaListaArticulos(ListView):
    '''
    Vista para listar los articulos publicados.
    '''

    model = Articulo
    template_name = 'blog/lista_articulos.html'
    context_object_name = 'articulos'
    ordering = ['-fecha_creacion']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        categoria_slug = self.request.GET.get('categoria')

        if query:
            queryset = queryset.filter(titulo__icontains=query)
        if categoria_slug:
            queryset = queryset.filter(categorias__slug=categoria_slug)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['categorias'] = Categoria.objects.all()
        categoria_slug = self.request.GET.get('categoria')
        context['categoria_actual'] = None
        if categoria_slug:
            context['categoria_actual'] = get_object_or_404(Categoria, slug=categoria_slug)
        return context

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