from django.test import TestCase, Client 
from django.urls import reverse
from .models import Articulo 

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


class PruebasVistasBlog(TestCase):
    """Pruebas para las vistas de la aplicación blog."""

    def setUp(self):
        """Configuración inicial para las pruebas de vistas."""
        self.client = Client() # Instancia del cliente de pruebas
        self.articulo1 = Articulo.objects.create(
            titulo="Artículo Uno", contenido="Contenido uno"
        )
        self.articulo2 = Articulo.objects.create(
            titulo="Artículo Dos", contenido="Contenido dos"
        )
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
        self.assertTemplateUsed(respuesta, 'blog/base.html') # Verifica que también usa la base

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
        """Verifica que la vista de detalle muestra el título y contenido del artículo."""
        respuesta = self.client.get(self.url_detalle_articulo1)
        self.assertContains(respuesta, "Artículo Uno")
        self.assertContains(respuesta, "Contenido uno")
        self.assertNotContains(respuesta, "Contenido dos")
    
    def test_vista_lista_articulos_busqueda_sin_termino_actual(self):
        """Verifica que sin término de búsqueda se muestran todos los artículos (los 2 existentes)."""
        respuesta = self.client.get(self.url_lista)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.articulo1.titulo)
        self.assertContains(respuesta, self.articulo2.titulo)
        self.assertEqual(len(respuesta.context['articulos']), 2)


    def test_vista_lista_articulos_busqueda_con_termino_existente(self):
        """Verifica que la búsqueda con un término que coincide con uno de los artículos filtra correctamente."""
        respuesta = self.client.get(self.url_lista, {'q': 'Uno'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.articulo1.titulo)
        self.assertNotContains(respuesta, self.articulo2.titulo)
        self.assertEqual(len(respuesta.context['articulos']), 1)

        respuesta = self.client.get(self.url_lista, {'q': 'Dos'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.articulo2.titulo)
        self.assertNotContains(respuesta, self.articulo1.titulo)
        self.assertEqual(len(respuesta.context['articulos']), 1)


    def test_vista_lista_articulos_busqueda_con_termino_inexistente_actual(self):
        """Verifica que la búsqueda con un término inexistente devuelve lista vacía."""
        respuesta = self.client.get(self.url_lista, {'q': 'Inexistente'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, self.articulo1.titulo)
        self.assertNotContains(respuesta, self.articulo2.titulo)
        self.assertContains(respuesta, "Todavía no hay artículos publicados") # Ajusta si tu texto es diferente
        self.assertEqual(len(respuesta.context['articulos']), 0)


    def test_vista_lista_articulos_busqueda_con_termino_vacio_actual(self):
        """Verifica que la búsqueda con un término vacío devuelve todos los artículos (los 2 existentes)."""
        respuesta = self.client.get(self.url_lista, {'q': ''})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, self.articulo1.titulo)
        self.assertContains(respuesta, self.articulo2.titulo)
        self.assertEqual(len(respuesta.context['articulos']), 2)

    def test_vista_lista_articulos_muestra_termino_buscado_actual(self):
        """Verifica que la plantilla muestra el término de búsqueda."""
        termino_buscado = "Uno" 
        respuesta = self.client.get(self.url_lista, {'q': termino_buscado})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, f"Resultados de búsqueda para: <strong>{termino_buscado}</strong>") 
        self.assertContains(respuesta, f'value="{termino_buscado}"')