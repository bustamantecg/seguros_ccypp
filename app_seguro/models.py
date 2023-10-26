from django.conf import settings
from django.db import models
from statistics import mode
from django.utils import timezone
from django.contrib.auth import get_user_model
from .choices import *
from django.utils.html import format_html
from .constants import DNI
from django.utils.functional import cached_property
from ckeditor.fields import RichTextField

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
# Create your models here.

Usuario = get_user_model()

def validate_eight_digits(value):
    if len(str(value)) < 5 or len(str(value)) > 8: 
        raise ValidationError('El número debe tener entre 6 y 8 dígitos.')
    
def validate_integer(value):
    if not value.isdigit():
        raise ValidationError("Ingrese solo números enteros")    

##-------------------------------------------------------------------------------------------------
class Saf(models.Model):
    nombre = models.CharField(max_length=80, verbose_name='Denoninación S.A.F.')
    nros = models.CharField(max_length=100, verbose_name='Nros. de S.A.F.', help_text='En caso de ser varios, separelos por coma')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "S.A.F."
        verbose_name_plural = "S.A.F."
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

class Tipodoc(models.Model):
    nombre = models.CharField(max_length=15, verbose_name="Tipo de Doc.", unique=True)
    abreviado = models.CharField(max_length=10, unique=True)
    
    class Meta:
        verbose_name = "Tipo de Doc."
        verbose_name_plural = "Tipo de Documentos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Provincia(models.Model):
    nombre = models.CharField(max_length=60, verbose_name="Provincia")
    iso_id = models.CharField(max_length=6)  
    latitud= models.CharField(max_length=14)
    longitud= models.CharField(max_length=14)
    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

##--------------------------------------------------------------------------
class Departamento(models.Model):
    nombre = models.CharField(max_length=60, verbose_name="Departamento")  
      
    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
##--------------------------------------------------------------------------
class Localidad(models.Model):
    nombre = models.CharField(max_length=60, verbose_name="Localidad")
    departamentos = models.ForeignKey(Departamento, on_delete=models.PROTECT, default=0, related_name='localidades')
    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
##--------------------------------------------------------------------------

class EstadoCivil(models.Model):
    nombre = models.CharField(max_length=20, verbose_name='Estado Civil')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estado Civil"
        verbose_name_plural = "Estado Civiles"
        ordering = ["nombre"]

    def __str__(self):
        return f'{self.nombre}'
##--------------------------------------------------------------------------

class Parentesco(models.Model):
    nombre = models.CharField(max_length=20, verbose_name='Parentesco', help_text="Ejemplo Hijo/a", unique=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Parentesco"
        verbose_name_plural = "Parentescos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

##--------------------------------------------------------------------------

class Organismo(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Organismo', unique=True, help_text="Por ejemplo: Ministerio, Municipalidad")
    domicilio = models.CharField(max_length=80)
    email = models.EmailField(max_length=254, help_text="Correo Electrónico", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Organismo"
        verbose_name_plural = "Organismos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

##--------------------------------------------------------------------------

class Oficina(models.Model):
    organismos = models.ForeignKey(Organismo, on_delete=models.PROTECT, help_text="Ministerio, Empresa")
    nombre = models.CharField(max_length=150, verbose_name='Oficina', unique=True)
    domicilio = models.CharField(max_length=80)
    email = models.EmailField(max_length=254, help_text="Correo Electrónico", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Oficina"
        verbose_name_plural = "Oficinas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    
##--------------------------------------------------------------------------

class Titular(models.Model):
    organismo = models.ForeignKey(Organismo, on_delete=models.PROTECT) 
    safs = models.ForeignKey(Saf, on_delete=models.PROTECT)
    apellido = models.CharField(max_length=35, verbose_name='Apellidos')
    nombre = models.CharField(max_length=35, verbose_name='Nombres')    
    tipodoc = models.ForeignKey(Tipodoc,on_delete=models.PROTECT, verbose_name='Tipo Doc.', default=1)
    nro = models.CharField(max_length=12, verbose_name='Número', help_text="Sin puntos, ni guiones", unique=True, validators=[validate_integer])    
    cuil = models.CharField(max_length=11, verbose_name='CUIL', help_text="Sin guiones", unique=True)
    sexo = models.CharField(max_length=1, choices=SEXO, default='F')    
    fecha_nacimiento = models.DateField(verbose_name='Fecha Nacimiento')
    email = models.EmailField(max_length=254, help_text="correo Electrónico", blank=True, null=True)
    domicilio = models.CharField(max_length=80)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT, verbose_name='Departamento')
    localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT)
    cp = models.CharField(max_length=10, verbose_name="Código Postal", help_text="Ejemplo 4700", default='4700')
    estado_civil = models.ForeignKey(EstadoCivil, on_delete=models.PROTECT, verbose_name='Estado Civil')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vive = models.BooleanField(default=True)
    discapacidad = models.BooleanField(default=False)
    situacion = models.CharField(max_length=8, choices=SITUACION, default='ACTIVO', verbose_name="Situación") # Activo; Jubilado        

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    edito = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Titular"
        verbose_name_plural = "Titulares"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f'{self.apellido}, {self.nombre} {self.cuil}'

    @cached_property
    def edad(self):
        edad = 0
        if self.fecha_nacimiento:
            dias_anual = 365.2425
            edad = int((timezone.now().date() - self.fecha_nacimiento).days / dias_anual)
        return edad

##--------------------------------------------------------------------------

class Seguro(models.Model):
    nombre = models.CharField(verbose_name="Seguro", max_length=100, help_text="Nombre del Seguro")
    descripcion = RichTextField(verbose_name='Descripción')
    legal = models.CharField(max_length=120, verbose_name="Ley/Decreto de Creación")
    activo = models.BooleanField(default=True)    
    requisito_ingreso = RichTextField(verbose_name="Requisitos de Ingreso", null=True, blank=True)
    requisito_cobro = RichTextField(verbose_name="Requisitos para Cobro", null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Seguro"
        verbose_name_plural = "Seguros"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre
##--------------------------------------------------------------------------    

class Preguntas_Frecuentes(models.Model):
    orden = models.IntegerField(default=1)
    pregunta = models.CharField(max_length=254)
    respuesta = models.CharField(max_length=254)
    activa = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pregunta Frecuente"
        verbose_name_plural = "Preguntas Frecuentes"
        ordering = ["orden"]

    def __str__(self):
        return f'{self.pregunta}'
    
##--------------------------------------------------------------------------    
class Requisito(models.Model):
    nombre = models.CharField(max_length=80, verbose_name="Requisito", unique=True)
    tipo = models.CharField(max_length=7, choices=OPCIONES, blank=True)
    seguros= models.ForeignKey(Seguro, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Requisito"
        verbose_name_plural = "Requisitos"

    def __str__(self):
        return self.nombre

##--------------------------------------------------------------------------    
class CargadorSeguro(models.Model):
    organismos = models.ForeignKey(Organismo, on_delete=models.PROTECT)
    oficinas = models.ForeignKey(Oficina, on_delete=models.PROTECT)
    agente_nro = models.CharField(max_length=20)
    apellido = models.CharField(max_length=35, verbose_name='Apellidos')
    nombre = models.CharField(max_length=35, verbose_name='Nombres')    
    tipodoc = models.ForeignKey(Tipodoc,on_delete=models.PROTECT, verbose_name='Tipo Doc.', default=1)
    nrodoc = models.CharField(max_length=12, verbose_name='D.N.I.', help_text="Sin puntos", unique=True, default=0)
    sexo = models.CharField(max_length=1, choices=SEXO, default='F')
    cuil = models.CharField(max_length=11, verbose_name='CUIL', help_text="Sin guiones", unique=True)
    fecha_nacimiento = models.DateField()
    email = models.EmailField(max_length=254, help_text="correo Electrónico", unique=True)
    cp = models.CharField(max_length=10, verbose_name="Código Postal", help_text="Ejemplo 4700")
    safs = models.ManyToManyField(Saf, verbose_name='S.A.F.')
    activo = models.BooleanField(default=False, verbose_name='Puede Cargar')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cargador de Seguros"
        verbose_name_plural = "Cargadores de Seguros"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return self.apellido+', '+self.nombre+', '+self.cuil
    
    @cached_property
    def edad(self):
        edad = 0
        if self.fecha_nacimiento:
            dias_anual = 365.2425
            edad = int((timezone.now().date() - self.fecha_nacimiento).days / dias_anual)
        return edad    


##--------------------------------------------------------------------------    
class Beneficiario(models.Model):
    titular = models.ForeignKey(Titular, on_delete=models.PROTECT)
    tipodoc = models.ForeignKey(Tipodoc,on_delete=models.PROTECT, verbose_name='Tipo Doc.', default=1) 
    nro = models.CharField(max_length=8, validators=[validate_integer])
    apellido = models.CharField(max_length=40, null=True, blank=True)
    nombres = models.CharField(max_length=40, null=True, blank=True)
    fecha_nacimiento = models.DateField()
    parentescos = models.ForeignKey(Parentesco, on_delete=models.SET_NULL, verbose_name='Relación de Parentesco', null=True, blank=True)
    domicilio = models.CharField(max_length=60, blank=True, null=True)
    barrio = models.CharField(max_length=60, null=True, blank=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT)
    email = models.EmailField(max_length=150, blank=True, null=True)
    created = models.DateField(auto_created=True, auto_now_add=True)
    updated = models.DateField(auto_now=True)
    
    seguro_vida = models.BooleanField(default=False, verbose_name="Seguro de Vida Obligatorio")
    seguro_facultativo = models.BooleanField(default=False, verbose_name="Seguro de Vida Facultativo Obligatorio")
    seguro_sepelio = models.BooleanField(default=False, verbose_name="Seguro de Sepelio")
    seguro_conyuge = models.BooleanField(default=False, verbose_name="Seguro de Vida Conyuge")
    subsidio_proteccion_flia = models.BooleanField(default=False, verbose_name="Subsidio de Protección a la Familia")

    operador = models.ForeignKey(Usuario, on_delete=models.PROTECT)

    class Meta:
        verbose_name = "Beneficiario"
        verbose_name_plural = "Beneficiarios"
        ordering = ["-id"]

    def __str__(self):
        return '%s (%s)' % (self.id, self.poliza)

    def tipoydoc(self):
        return f'{self.tipodoc}: {self.nro}'
    
    @cached_property
    def edad(self):
        edad = 0
        if self.fecha_nacimiento:
            dias_anual = 365.2425
            edad = int((timezone.now().date() - self.fecha_nacimiento).days / dias_anual)
        return edad    

##--------------------------------------------------------------------------    
class Contacto(models.Model):
    nombre = models.CharField(max_length=100)    
    email = models.EmailField(max_length=250)
    mensaje = models.TextField(max_length=250)

