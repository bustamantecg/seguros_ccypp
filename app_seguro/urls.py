from django import views
from django.conf.urls import handler404
from django.contrib.auth import views as auth_views
from django.urls import path
from app_seguro.views import *


urlpatterns = [
    path('', index, name='index'), 

    #path('edit_profile/', views.edit_profile, name='edit_profile'), #  17/08/2023 ok
    path('mi_profile/', mi_profile, name='mi_profile'),
    path('contacto/', contacto, name='contacto'),   
    path('contacto_recibido/', contacto_recibido, name='contacto_recibido'),

    path('seguros/', seguros, name='seguros'), # OK
        
# interactua con la lista de Dptos
    path('get_localidades/<int:depto_id>/', get_localidades, name='get_localidades'), 

    path('titulares/', titulares, name='titulares'), # Buscador de Titular (Nuevo, Edita, Detalles)     
    path('titular_nuevo/', titular_nuevo, name='titular_nuevo'),  # Graba Titular y llama titular_detalle
    path('titular_detalle/<int:id>', titular_detalle, name='titular_detalle'), ## ID del titular Muestra info del Titular y LLama a Beneficiario_Nuevo
    path('titular_editar/<int:id>', titular_editar, name='titular_editar'),  
    
    path('beneficiario_nuevo/<int:id>', beneficiario_nuevo, name='beneficiario_nuevo'),   ## ID del titular 
    path('beneficiario_editar/<int:id>', beneficiario_editar, name='beneficiario_editar'),   ## ID del Benef     
    path('beneficiario_eliminar/<int:benef_id>/', beneficiario_eliminar, name='beneficiario_eliminar'),

    # Reportes
    path('Pdf_comprobante_titular/<int:id>', Pdf_comprobante_titular.as_view(), name='Pdf_comprobante_titular'),
    path('pdf_seguro_vida/<int:id>', pdf_seguro_vida.as_view(), name='pdf_seguro_vida'),
    path('pdf_seguro_sepelio/<int:id>', pdf_seguro_sepelio.as_view(), name="pdf_seguro_sepelio"),
    path('pdf_seguro_facultativo/<int:id>', pdf_seguro_facultativo.as_view(), name="pdf_seguro_facultativo"),
    path('pdf_seguro_conyuge/<int:id>', pdf_seguro_conyuge.as_view(), name="pdf_seguro_conyuge"),
    path('pdf_seguro_familia/<int:id>', pdf_seguro_familia.as_view(), name="pdf_seguro_familia"),
    path('pdf_seguro_todos/<int:id>', pdf_seguro_todos.as_view(), name="pdf_seguro_todos"),
    
    #EMail ****************************************
    path('email_comprobante_seguro/<int:id>', email_comprobante_seguro.as_view(), name="email_comprobante_seguro"),       
]  

handler404 = 'app_seguro.views.pagina_no_encontrada'




# --------------------- opciones del Asegurado ---------------------------------------------------------------------------------
    #path('mis_polizas/', views.mis_polizas, name='mis_polizas'),
    #path('mis_beneficiarios/<int:poliza_id>', views.mis_beneficiarios, name='mis_beneficiarios'),
    
# --------------------- opciones Con  Cargadores -------------------------------------------------------------------------------
    #path('cargador_buscar/', views.cargador_buscar, name='cargador_buscar'),  # OK - Inicia pasos de Registro de Polizas    
    #path('cargador_nuevo/', views.cargador_nuevo, name='cargador_nuevo'),       # ok
    #path('cargador_editar/<int:id>', views.cargador_editar, name='cargador_editar'), # Ver tema fecha_Nacimiento: no trae por el widgets <-------------------
    #path('cargador_detalle/<int:id>', views.cargador_detalle, name='cargador_detalle'), # falta organismo de trabajo<-------------------   

    #----------- APIS -----------------------------------------------------------------------------------------------------
    #path('api_renaper/', api_renaper, name='api_renaper'),
    #path('obtner_renaper/', obtner_renaper, name='obtner_renaper'),
