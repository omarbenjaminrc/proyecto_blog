from django.test import TestCase, Client 
from django.urls import reverse
from .models import Articulo, Categoria
from django.db.utils import IntegrityError 
from django.shortcuts import get_object_or_404 
from django.db import models

class PruebasModeloArticulo(TestCase):
    """Pruebas para el modelo Articulo."""

    def setUp(self):
        """Crea un objeto Articulo para usar en las pruebas del modelo."""
        self.articulo = Articulo.objects.create(
            titulo="Un Título de Prueba",
            contenido="Este es el contenido del artículo de prueba."
        )

    def test_representacion_str(self):
        """Verifica que el método __str__ devuelve el título."""
        self.assertEqual(str(self.articulo), "Un Título de Prueba")

    def test_generacion_slug(self):
        """Verifica que el slug se genera correctamente al guardar."""
        self.assertIsNotNone(self.articulo.slug)
        self.assertEqual(self.articulo.slug, "un-titulo-de-prueba")

    def test_get_absolute_url(self):
        """Verifica que get_absolute_url devuelve la URL correcta."""
        url_esperada = reverse('blog:detalle_articulo', kwargs={'slug': self.articulo.slug})
        self.assertEqual(self.articulo.get_absolute_url(), url_esperada)

    def test_campo_categorias_existe(self):
        """Verifica que el modelo Articulo tiene un campo 'categorias'."""
        field = Articulo._meta.get_field('categorias')
        self.assertTrue(isinstance(field, models.ManyToManyField))

class PruebasModeloCategoria(TestCase):
    """Pruebas para el modelo Categoria."""

    def setUp(self):
        """Crea un objeto Categoria para usar en las pruebas."""
        self.categoria = Categoria.objects.create(nombre="Tecnología")

    def test_representacion_str(self):
        """Verifica que el método __str__ devuelve el nombre."""
        self.assertEqual(str(self.categoria), "Tecnología")

    def test_generacion_slug(self):
        """Verifica que el slug de categoría se genera correctamente al guardar."""
        self.assertIsNotNone(self.categoria.slug)
        self.assertEqual(self.categoria.slug, "tecnologia")

    def test_no_crear_categoria_nombre_duplicado(self):
        """Verifica que no se puede crear una categoría con nombre duplicado."""
        with self.assertRaises(IntegrityError):
            Categoria.objects.create(nombre="Tecnología") # Nombre duplicado

    def test_no_crear_categoria_slug_duplicado(self):
        """Verifica que no se puede crear una categoría con slug duplicado."""
        Categoria.objects.create(nombre="Otra Categoría", slug="slug-manual")
        with self.assertRaises(IntegrityError):
            Categoria.objects.create(nombre="Tercera Categoría", slug="slug-manual")

class PruebasVistasBlog(TestCase):
    """Pruebas para las vistas de la aplicación blog."""

    def setUp(self):
        """Configuración inicial para las pruebas de vistas."""
        self.client = Client() 

        self.articulo1 = Articulo.objects.create(
            titulo="Artículo Uno: Introducción a Django", contenido="Contenido sobre Django"
        )
        self.articulo2 = Articulo.objects.create(
            titulo="Artículo Dos: Pruebas Unitarias", contenido="Contenido sobre Pruebas"
        )
        self.articulo3 = Articulo.objects.create(
            titulo="Artículo Tres: Django Avanzado", contenido="Más sobre Django"
        )
        self.articulo4 = Articulo.objects.create(
            titulo="Artículo Cuatro: Desarrollo Ágil", contenido="Sobre metodologías ágiles"
        )

        # Categorías de prueba
        self.categoria_tecnologia = Categoria.objects.create(nombre="Tecnología")
        self.categoria_tutoriales = Categoria.objects.create(nombre="Tutoriales")
        self.categoria_metodologia = Categoria.objects.create(nombre="Metodología")

        # Asignar categorías a los artículos
        self.articulo1.categorias.add(self.categoria_tecnologia, self.categoria_tutoriales)
        self.articulo2.categorias.add(self.categoria_tutoriales, self.categoria_metodologia)
        self.articulo3.categorias.add(self.categoria_tecnologia)
        # Articulo4 no tiene categorías

        # URLs existentes
        self.url_lista = reverse('blog:lista_articulos')
        self.url_detalle_articulo1 = reverse('blog:detalle_articulo', kwargs={'slug': self.articulo1.slug})
        self.url_detalle_inexistente = reverse('blog:detalle_articulo', kwargs={'slug': 'slug-que-no-existe'})

    def test_vista_lista_articulos_status_code(self):
        """Verifica que la vista de lista devuelve un status 200 OK."""
        respuesta = self.client.get(self.url_lista)
        self.assertEqual(respuesta.status_code, 200)

    def test_vista_lista_articulos_template_usado(self):
        """Verifica que la vista de lista usa la plantilla correcta."""
        respuesta = self.client.get(self.url_lista)
        self.assertTemplateUsed(respuesta, 'blog/lista_articulos.html')
        self.assertTemplateUsed(respuesta, 'blog/base.html') 

    def test_vista_lista_articulos_contiene_articulos(self):
        """Verifica que la vista de lista muestra los títulos de los artículos."""
        respuesta = self.client.get(self.url_lista)
        self.assertContains(respuesta, "Artículo Uno")
        self.assertContains(respuesta, "Artículo Dos")

    def test_vista_detalle_articulo_status_code(self):
        """Verifica que la vista de detalle devuelve 200 OK para un slug existente."""
        respuesta = self.client.get(self.url_detalle_articulo1)
        self.assertEqual(respuesta.status_code, 200)

    def test_vista_detalle_articulo_status_code_404(self):
        """Verifica que la vista de detalle devuelve 404 para un slug inexistente."""
        respuesta = self.client.get(self.url_detalle_inexistente)
        self.assertEqual(respuesta.status_code, 404)

    def test_vista_detalle_articulo_template_usado(self):
        """Verifica que la vista de detalle usa la plantilla correcta."""
        respuesta = self.client.get(self.url_detalle_articulo1)
        self.assertTemplateUsed(respuesta, 'blog/detalle_articulo.html')
        self.assertTemplateUsed(respuesta, 'blog/base.html')

    def test_vista_detalle_articulo_muestra_contenido(self):
        """Verifica que la vista de detalle muestra solo el título y contenido del artículo solicitado."""
        respuesta = self.client.get(self.url_detalle_articulo1)
        self.assertEqual(respuesta.status_code, 200) # Asegurarse de que carga bien

        # Verifica que el contenido del articulo1 ESTÁ presente
        self.assertContains(respuesta, self.articulo1.titulo)
        self.assertContains(respuesta, self.articulo1.contenido)

        # Verifica que el contenido de los OTROS artículos NO está presente
        self.assertNotContains(respuesta, self.articulo2.titulo)
        self.assertNotContains(respuesta, self.articulo2.contenido)
        self.assertNotContains(respuesta, self.articulo3.titulo)
        self.assertNotContains(respuesta, self.articulo3.contenido)
        self.assertNotContains(respuesta, self.articulo4.titulo)
        self.assertNotContains(respuesta, self.articulo4.contenido)
    
    def test_vista_lista_articulos_busqueda_sin_termino(self):
        """Verifica que sin término de búsqueda ni filtro de categoría se muestran todos los artículos (los 4)."""
        respuesta = self.client.get(self.url_lista)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.articulo1.titulo)
        self.assertContains(respuesta, self.articulo2.titulo)
        self.assertContains(respuesta, self.articulo3.titulo)
        self.assertContains(respuesta, self.articulo4.titulo)
        self.assertEqual(len(respuesta.context['articulos']), 4)


    def test_vista_lista_articulos_busqueda_con_termino_existente(self):
        """Verifica que la búsqueda por título filtra correctamente."""
        respuesta = self.client.get(self.url_lista, {'q': 'Django'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.articulo1.titulo) # Contiene "Django"
        self.assertContains(respuesta, self.articulo3.titulo) # Contiene "Django"
        self.assertNotContains(respuesta, self.articulo2.titulo) # No contiene "Django"
        self.assertNotContains(respuesta, self.articulo4.titulo) # No contiene "Django"
        self.assertEqual(len(respuesta.context['articulos']), 2)


    def test_vista_lista_articulos_busqueda_con_termino_inexistente(self):
        """Verifica que la búsqueda con un término inexistente devuelve lista vacía y mensaje correcto."""
        respuesta = self.client.get(self.url_lista, {'q': 'Inexistente'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, self.articulo1.titulo)
        self.assertNotContains(respuesta, self.articulo2.titulo)
        self.assertNotContains(respuesta, self.articulo3.titulo)
        self.assertNotContains(respuesta, self.articulo4.titulo)
        self.assertContains(respuesta, 'No se encontraron artículos para "Inexistente".') # Mensaje de tu plantilla
        self.assertEqual(len(respuesta.context['articulos']), 0)

    def test_vista_lista_articulos_busqueda_con_termino_vacio(self):
        """Verifica que la búsqueda con un término vacío devuelve todos los artículos."""
        respuesta = self.client.get(self.url_lista, {'q': ''})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.articulo1.titulo)
        self.assertContains(respuesta, self.articulo2.titulo)
        self.assertContains(respuesta, self.articulo3.titulo)
        self.assertContains(respuesta, self.articulo4.titulo)
        self.assertEqual(len(respuesta.context['articulos']), 4)

    def test_vista_lista_articulos_muestra_termino_buscado(self):
        """Verifica que la plantilla muestra el término de búsqueda."""
        termino_buscado = "Django"
        respuesta = self.client.get(self.url_lista, {'q': termino_buscado})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, f'Resultados de búsqueda para: "{termino_buscado}"') # Mensaje de tu plantilla
        self.assertContains(respuesta, f'value="{termino_buscado}"')

    def test_vista_lista_articulos_filtro_categoria_existente(self):
        """Verifica que el filtrado por categoría existente funciona correctamente."""
        # Filtramos por la categoría 'tecnologia'
        respuesta = self.client.get(self.url_lista, {'categoria': self.categoria_tecnologia.slug})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.articulo1.titulo) # Tiene Tecnología
        self.assertContains(respuesta, self.articulo3.titulo) # Tiene Tecnología
        self.assertNotContains(respuesta, self.articulo2.titulo) # No tiene Tecnología
        self.assertNotContains(respuesta, self.articulo4.titulo) # No tiene Tecnología
        self.assertEqual(len(respuesta.context['articulos']), 2)
        self.assertContains(respuesta, f'Artículos en la categoría: "{self.categoria_tecnologia.nombre}"')
        self.assertEqual(respuesta.context['categoria_actual'], self.categoria_tecnologia)


    def test_vista_lista_articulos_filtro_categoria_inexistente(self):
        """Verifica que el filtrado por categoría inexistente devuelve 404."""
        respuesta = self.client.get(self.url_lista, {'categoria': 'slug-categoria-inexistente'})
        self.assertEqual(respuesta.status_code, 404)

    def test_vista_lista_articulos_filtro_categoria_sin_articulos(self):
        """Verifica que el filtrado por una categoría existente sin artículos devuelve lista vacía y mensaje correcto."""
        categoria_vacia = Categoria.objects.create(nombre="Categoria Vacia")
        respuesta = self.client.get(self.url_lista, {'categoria': categoria_vacia.slug})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, self.articulo1.titulo)
        self.assertNotContains(respuesta, self.articulo2.titulo)
        self.assertNotContains(respuesta, self.articulo3.titulo)
        self.assertNotContains(respuesta, self.articulo4.titulo)
        self.assertContains(respuesta, f'No hay artículos en la categoría "{categoria_vacia.nombre}".') 
        self.assertEqual(len(respuesta.context['articulos']), 0)
        self.assertEqual(respuesta.context['categoria_actual'], categoria_vacia)


    def test_vista_lista_articulos_filtro_categoria_vacio(self):
        """Verifica que el filtro con parámetro 'categoria' vacío devuelve todos los artículos."""
        respuesta = self.client.get(self.url_lista, {'categoria': ''})
        self.assertEqual(respuesta.status_code, 200)
        # Debe mostrar todos los artículos 
        self.assertContains(respuesta, self.articulo1.titulo)
        self.assertContains(respuesta, self.articulo2.titulo)
        self.assertContains(respuesta, self.articulo3.titulo)
        self.assertContains(respuesta, self.articulo4.titulo)
        self.assertEqual(len(respuesta.context['articulos']), 4)
        # Verifica que categoria_actual NO está en el contexto o es None
        self.assertIsNone(respuesta.context.get('categoria_actual'))


    #  TESTS PARA COMBINAR BÚSQUEDA Y FILTRO DE CATEGORÍA 

    def test_vista_lista_articulos_busqueda_y_filtro_combinado(self):
        """Verifica que la búsqueda por título Y filtrado por categoría combinados funcionan."""
        
        respuesta = self.client.get(self.url_lista, {'q': 'Django', 'categoria': self.categoria_tecnologia.slug})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.articulo1.titulo)
        self.assertContains(respuesta, self.articulo3.titulo)
        self.assertNotContains(respuesta, self.articulo2.titulo)
        self.assertNotContains(respuesta, self.articulo4.titulo)
        self.assertEqual(len(respuesta.context['articulos']), 2)
        self.assertEqual(respuesta.context['categoria_actual'], self.categoria_tecnologia)
        self.assertEqual(respuesta.context['query'], 'Django')

    
        respuesta = self.client.get(self.url_lista, {'q': 'Pruebas', 'categoria': self.categoria_tutoriales.slug})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, self.articulo1.titulo)
        self.assertContains(respuesta, self.articulo2.titulo)
        self.assertNotContains(respuesta, self.articulo3.titulo)
        self.assertNotContains(respuesta, self.articulo4.titulo)
        self.assertEqual(len(respuesta.context['articulos']), 1)
        self.assertEqual(respuesta.context['categoria_actual'], self.categoria_tutoriales)
        self.assertEqual(respuesta.context['query'], 'Pruebas')


    def test_vista_lista_articulos_busqueda_existente_filtro_inexistente(self):
        """Verifica que búsqueda existente + filtro de categoría inexistente devuelve 404."""
        respuesta = self.client.get(self.url_lista, {'q': 'Django', 'categoria': 'slug-inexistente'})
        self.assertEqual(respuesta.status_code, 404)

    def test_vista_lista_articulos_busqueda_inexistente_filtro_existente(self):
        """Verifica que búsqueda inexistente + filtro de categoría existente devuelve lista vacía y mensaje correcto."""
        respuesta = self.client.get(self.url_lista, {'q': 'Inexistente', 'categoria': self.categoria_tecnologia.slug})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, self.articulo1.titulo)
        self.assertNotContains(respuesta, self.articulo2.titulo)
        self.assertNotContains(respuesta, self.articulo3.titulo)
        self.assertNotContains(respuesta, self.articulo4.titulo)
        self.assertContains(respuesta, f'No hay artículos en la categoría "{self.categoria_tecnologia.nombre}".') 
        self.assertEqual(len(respuesta.context['articulos']), 0)
        self.assertEqual(respuesta.context['categoria_actual'], self.categoria_tecnologia)
        self.assertEqual(respuesta.context['query'], 'Inexistente') 