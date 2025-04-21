from django.db import models
from django.utils.text import slugify

class Articulo(models.Model):
    titulo = models.CharField(max_length= 90)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=100,unique=True,db_index=True,blank=True)

    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs): 
        '''
        Sobrescribe el método save original.
        Crea un slug automaticamente si no existe uno al guardar el articulo.
        '''
        if not self.slug: 
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs) 

    def get_absolute_url(self):
        '''
        Devuelve la URL absoluta para una instancia de Articulo.
        '''
        from django.urls import reverse
        
        return reverse('detalle_articulo', kwargs={'slug': self.slug})