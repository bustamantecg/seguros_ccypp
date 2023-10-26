from django.contrib import admin
from .models import *


# Register your models here.
class SafAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nros', 'created', 'updated')
    readonly_fields = ('created', 'updated')
    list_filter = ("created", 'updated')

class TipodocAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviado', 'id')

class EstadoCivilAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    readonly_fields = ('created', 'updated')

class ParentescoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    readonly_fields = ('created', 'updated')

class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    
class LocalidadAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "departamentos")
    search_fields = ("nombre",)
    list_filter=("departamentos",)

    @admin.display(ordering='nombre')
    def departamentos(self, obj):
        return obj.profile.departamentos    

class OrganismoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "email", 'domicilio', 'updated')
    search_fields = ("id", "nombre")
    readonly_fields = ('id', 'created', 'updated')

class OficinaAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", 'organismos', "email", 'domicilio', 'updated')
    search_fields = ("id", "nombre", 'created')
    readonly_fields = ('id', 'created', 'updated')
#----------------------------------------------------------------------------------------

class SeguroAdmin(admin.ModelAdmin):
    list_display = ("id", "activo", "nombre", "legal", "descripcion")
    list_filter = ("nombre", 'activo')
    search_fields = ("nombre", "legal")
    readonly_fields = ("id", 'created', 'updated')

class RequisitoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "tipo")
    search_fields = ("nombre", "id", "Tipo")

class CargadorSeguroAdmin(admin.ModelAdmin):
    list_display = ("id", "activo", "apellido", "nombre", "cuil", "oficinas")
    search_fields = ("id", "cuil", "apellido", "oficina")
    list_filter = ('activo', "sexo", "updated", 'safs')
    readonly_field = ("id", 'created', 'updated')

class TitularBeneficiarioInline(admin.TabularInline):
    model = Beneficiario

class TitularAdmin(admin.ModelAdmin):
    readonly_fields = ('created', 'updated')
    list_display = ("cuil", "apellido", "nombre", "sexo", 'updated', 'edad', 'tipodoc','nro','created')
    list_filter = ("cp", 'updated')
    search_fields = ("apellido", "cp", 'updated')
    inlines = [TitularBeneficiarioInline]   

class Preguntas_FrecuentesAdmin(admin.ModelAdmin):
    list_display = ('orden', 'activa', 'pregunta', 'respuesta')
    list_filter = ('created', 'updated')


class BeneficiarioAdmin(admin.ModelAdmin):
    list_display = ('tipoydoc', 'apellido', 'nombres', 'edad', 'parentescos', 'seguro_vida', 'seguro_facultativo', 'seguro_sepelio', 'seguro_conyuge', 'subsidio_proteccion_flia', 'titular', 'operador')
    readonly_field = ("id", 'created')
    list_filter = ('parentescos', 'departamento', 'created')
    search_fields = ("id", 'nro', 'apellido')  

#-------------------------------------------------------------------------------------------
admin.site.register(Saf, SafAdmin)
admin.site.register(Tipodoc, TipodocAdmin)
admin.site.register(EstadoCivil, EstadoCivilAdmin)
admin.site.register(Parentesco, ParentescoAdmin)
admin.site.register(Titular, TitularAdmin)
admin.site.register(Departamento, DepartamentoAdmin)
admin.site.register(Localidad, LocalidadAdmin)
admin.site.register(Organismo, OrganismoAdmin)
admin.site.register(Oficina,OficinaAdmin)

admin.site.register(Seguro, SeguroAdmin)
admin.site.register(Requisito, RequisitoAdmin)
admin.site.register(CargadorSeguro, CargadorSeguroAdmin)
admin.site.register(Preguntas_Frecuentes, Preguntas_FrecuentesAdmin)
admin.site.register(Beneficiario, BeneficiarioAdmin)