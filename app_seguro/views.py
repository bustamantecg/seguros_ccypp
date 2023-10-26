import smtplib
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.views import PasswordChangeView

from django.urls import reverse_lazy
from django.views.generic import View
import datetime

import os
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa
from django.core.mail import EmailMessage


from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Create your views here.
from accounts.models import Profile
from django.http import JsonResponse
from .forms import BeneficiarioForm, ContactoForm, TitularForm
from .models import Titular, Beneficiario, Seguro, Localidad

## ------------------------------------------------------------------------------------------------
def pagina_no_encontrada(request, exception):
    return render(request, '404.html', status=404)

def index(request):
    seguros = Seguro.objects.filter(activo=True)
    return render(request, "app_seguro/index.html", {'seguros':seguros})

@login_required
def change_password(request):
    return PasswordChangeView.as_view(
        template_name='registration/change_password.html',  # La plantilla HTML para el formulario
        success_url=reverse_lazy('index')  # URL a la que redirigir después de cambiar la contraseña
    )(request)


def mi_profile(request):       
    usuario = request.user  
    user_groups = request.user.groups.all()
    usuario_log = get_object_or_404(Profile, user=request.user)
    safs = usuario_log.safs.all()
        
    return render(request, 'registration/mi_profile.html', {'usuario_log':usuario_log,
                                                            'safs':safs,
                                                            'usuario':usuario,
                                                            'user_groups':user_groups})


def contacto(request):
    contacto_form = ContactoForm()
    if request.method=='POST':
        contacto_form=ContactoForm(request.POST)
        if contacto_form.is_valid():
            contacto_form.save()
            messages.success(request,'Gracias por Contactarnos')
        else:
            messages.error(request, 'Atención: Verifique los Dastos Ingresados')    

    return render(request, 'app_seguro/contacto.html', {'contacto_form':contacto_form})

## ------------------------------------------------------------------------------------------------
def seguros(request):    
    seguros = Seguro.objects.filter(activo=True)
    return render(request, 'app_seguro/listado.html', {'seguros':seguros})

def get_localidades(request, depto_id):
    localidades = Localidad.objects.filter(departamentos_id=depto_id)
    localidades_data = [{'id': localidad.id, 'nombre': localidad.nombre} for localidad in localidades]
    return JsonResponse(localidades_data, safe=False)

#### -------------------- Accesos del los Titulares -------------------------------------
@login_required
def titulares(request):
    busqueda = request.POST.get('buscar')
    opcion = request.POST.get('opcion')    
    usuario = request.user # obtengo usuario loguado
    aseguradores_group = Group.objects.get(name='Empleados') # Obtenemos el grupo "Aseguradores" 
    print(aseguradores_group)
    if aseguradores_group in usuario.groups.all():
        is_empleado= True 
    else:
        is_empleado= False

    if busqueda:
        if opcion == 'idtitular':
            if is_empleado:
                titulares = Titular.objects.filter(id__icontains=busqueda)
            else:
                titulares = Titular.objects.filter(safs__in=usuario.profile.safs.all(), id__icontains=busqueda)

        elif opcion == 'dni':
            if is_empleado:
                titulares = Titular.objects.filter(nro__contains=busqueda)
            else:    
                titulares = Titular.objects.filter(safs__in=usuario.profile.safs.all(), nro__contains=busqueda)

        elif opcion == 'cuil':            
            if is_empleado:
                titulares = Titular.objects.filter(cuil__icontains=busqueda)
            else:
                titulares = Titular.objects.filter(safs__in=usuario.profile.safs.all(), cuil__icontains=busqueda)

        elif opcion == 'apenom':            
            if is_empleado:
                titulares = Titular.objects.filter(apellido__icontains=busqueda).order_by('apellido', 'nombre')
            else:
                titulares = Titular.objects.filter(safs__in=usuario.profile.safs.all(), apellido__icontains=busqueda).order_by('apellido', 'nombre')                    

        elif opcion == 'email':
            if is_empleado:
                titulares = Titular.objects.filter(email__icontains=busqueda).order_by('apellido', 'nombre')
            else:    
                titulares = Titular.objects.filter(safs__in=usuario.profile.safs.all(), email__icontains=busqueda).order_by('apellido', 'nombre')
        encontradas = len(titulares)        
    else:
        titulares = ""
        encontradas = -1    
    return render(request, 'app_seguro/titulares.html', {'titulares': titulares, 'encontradas': encontradas})    


@login_required
def titular_detalle(request, id):
    titular = get_object_or_404(Titular, pk=id)    
    beneficiarios = Beneficiario.objects.filter(titular__id=id)        
    return render(request, 'app_seguro/titular_detalle.html', {'titular':titular, 'beneficiarios':beneficiarios})

@login_required 
def titular_editar(request, id):
    titular = get_object_or_404(Titular, pk=id)    
    fecha_nacimiento_str = titular.fecha_nacimiento.strftime('%Y-%m-%d')
    titular.fecha_nacimiento=fecha_nacimiento_str    
    formatitular = TitularForm(instance=titular)    
    if request.method == 'POST':
        formatitular = TitularForm(request.POST, instance=titular)        
        if formatitular.is_valid():
            ftitular_nueva = formatitular.save(commit=False)
            #if request.user.is_superuser:
            ftitular_nueva.edito = request.user.id
            ftitular_nueva.save()            
            messages.success(request, 'Titular Editado Correctamente')
            #return redirect('titular_detalle', id=titular.id)
            return redirect('titulares')
        else:
            messages.error(request, 'Hubo un error en el formulario. Por favor, corrige los errores.') 
    else:
        user_safs = request.user.profile.safs.all()
        formatitular.fields['safs'].queryset = user_safs    
    return render(request, 'app_seguro/titular_editar.html' ,{'formatitular':formatitular})
    
@login_required
def titular_nuevo(request):    
    mensajes = ''    
    formtitular = TitularForm()    
    if request.method == 'POST':
        formtitular = TitularForm(request.POST)
        if formtitular.is_valid():
            new_Titular = formtitular.save(commit=False)
            new_Titular.usuario = get_object_or_404(User, pk=request.user.id)
            ExisteTitular = Titular.objects.filter(cuil=new_Titular.cuil)
            if ExisteTitular:
                messages.error(request, 'Ya Existe un Titular Registrado con CUIL '+str(new_Titular.cuil))
            else:
                new_Titular.situacion = "Activo"                
                new_Titular.save()
                id = new_Titular.pk
                messages.success(request, 'Titular Registrado Correctamente ID:' + str(id))
                return redirect('titular_detalle', id=id)  # Redirige a la vista de detalle con el ID
        else:            
            messages.error(request, 'Hubo un error en el formulario. Por favor, corrige los errores.')  # Mensaje de error
    
    user_safs = request.user.profile.safs.all()       
    formtitular.fields['safs'].queryset = user_safs            
    return render(request, 'app_seguro/titular_nuevo.html', {'formtitular': formtitular, 'mensaje': mensajes})

@login_required
def beneficiario_nuevo(request, id):        
    titular = Titular.objects.get(id=id) 
    if request.method == 'POST':
        form_Beneficiario = BeneficiarioForm(request.POST)
        if form_Beneficiario.is_valid():
            new_Benef = form_Beneficiario.save(commit=False)  
            new_Benef.operador_id = request.user.id
            new_Benef.titular_id = id
            new_Benef.save()
            messages.success(request, 'Beneficiario Registrado Correctamente')             
            return redirect('titular_detalle', id=id)           
    else:    
        #opciones_parentesco = Beneficiario.objects.exclude(parentescos__nombre='Heredero Forzoso')    
        form_Beneficiario = BeneficiarioForm()        
        
        #form_Beneficiario.fields['parentescos'].queryset = opciones_parentesco
        #print(opciones_parentesco)

    return render(request, 'app_seguro/beneficiario_nuevo.html', {'form_Beneficiario':form_Beneficiario, 'titular':titular})


@login_required
def beneficiario_editar(request, id):
    benef = get_object_or_404(Beneficiario, pk=id)    
    fecha_nacimiento_str = benef.fecha_nacimiento.strftime('%Y-%m-%d')
    benef.fecha_nacimiento=fecha_nacimiento_str        
    form_Beneficiario = BeneficiarioForm(instance=benef)
    titular= Titular.objects.get(id=benef.titular_id) 
    if request.method == 'POST':
        form_Beneficiario = BeneficiarioForm(request.POST, instance=benef)
        if form_Beneficiario.is_valid():
            form_Beneficiario.save()
            return redirect('titular_detalle', id=benef.titular_id)
        else:
            messages.error(request, 'Error: Por favor verifique los datos ingresados')            
    return render(request, 'app_seguro/beneficiario_editar.html', {'form_Beneficiario':form_Beneficiario, 'titular':titular})        


@login_required
def beneficiario_eliminar(request, benef_id):
    borrar_Benef = get_object_or_404(Beneficiario, pk=benef_id)
    titular_id = borrar_Benef.titular.id
    borrar_Benef.delete()
    return redirect('titular_detalle', titular_id)    

#****************** REPORTES a PDF **********************************************************************************************

class Pdf_comprobante_titular(View):
    def link_callback(self, uri, rel):
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri
            # make sure that file exists
        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))
        return path
    
    def get(self, request, id, **kwargs):
        try:
            fecha_actual = datetime.datetime.now()
            usuario = request.user   
            template = get_template('app_seguro/pdf_titular_comprobante.html')
            titular= Titular.objects.get(pk=id, safs__in=usuario.profile.safs.all())
            context = {'titular':titular, 
                       'usuario':usuario,
                       'fecha_actual':fecha_actual,
                       'logo':'{}{}'.format(settings.STATIC_URL, 'assets/img/logo_horizontal.png')
                       } # si la imagen esta en la carpeta media: se cambia STATIC_URL por MEDIA_URL
            html=template.render(context)
            response = HttpResponse(content_type='application/pdf')
            #la linea siguiente: descarga directamente el pdf generado; si lo omito como ahora, me muestra el pdf
            #response['Content-Disposition'] = 'attachment; filename="Comprobante_Seguro_Titular.pdf"'        
            
            pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)     
            return response
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('titulares'))
    
class pdf_seguro_vida(View):

    def link_callback(self, uri, rel):
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

            # make sure that file exists
        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))       
        return path
    
    def get(self, request, id, **kwargs):        
        try:        
            fecha_actual = datetime.datetime.now()
            usuario = request.user           
            template = get_template('app_seguro/pdf_seguro_vida.html')            
            #titular= Titular.objects.get(pk=id, safs__in=usuario.profile.safs.all())    
            titular= Titular.objects.get(pk=id)    
            beneficiarios = Beneficiario.objects.filter(titular=titular, seguro_vida=True)
            
            context = {'titular':titular, 
                       'usuario':usuario,
                       'fecha_actual':fecha_actual,                     
                       'beneficiarios':beneficiarios,
                       'logo':'{}{}'.format(settings.STATIC_URL, 'assets/img/logo_horizontal.png')
                       }
            html=template.render(context)
            response = HttpResponse(content_type='application/pdf')
            #la linea siguiente: descarga directamente el pdf generado
            #response['Content-Disposition'] = 'attachment; filename="Comprobante_Seguro_Vida.pdf"'                   
            pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)     
            return response
        except:            
            pass            
        return HttpResponseRedirect(reverse_lazy('titulares'))

class pdf_seguro_sepelio(View):

    def link_callback(self, uri, rel):
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

            # make sure that file exists
        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))       
        return path
    
    def get(self, request, id, **kwargs):        
        try:        
            fecha_actual = datetime.datetime.now()
            usuario = request.user           
            template = get_template('app_seguro/pdf_seguro_sepelio.html')            
            #titular= Titular.objects.get(pk=id, safs__in=usuario.profile.safs.all())    
            titular= Titular.objects.get(pk=id)    
            beneficiarios = Beneficiario.objects.filter(titular=titular, seguro_sepelio=True)
            
            context = {'titular':titular, 
                       'usuario':usuario,
                       'fecha_actual':fecha_actual,                     
                       'beneficiarios':beneficiarios,
                       'logo':'{}{}'.format(settings.STATIC_URL, 'assets/img/logo_horizontal.png')
                       }
            html=template.render(context)
            response = HttpResponse(content_type='application/pdf')
            #la linea siguiente: descarga directamente el pdf generado
            #response['Content-Disposition'] = 'attachment; filename="Comprobante_Seguro_Vida.pdf"'                   
            pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)     
            return response
        except:            
            pass            
        return HttpResponseRedirect(reverse_lazy('titulares'))

class pdf_seguro_facultativo(View):
    def link_callback(self, uri, rel):
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

            # make sure that file exists
        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))       
        return path
    
    def get(self, request, id, **kwargs):        
        try:        
            fecha_actual = datetime.datetime.now()
            usuario = request.user           
            template = get_template('app_seguro/pdf_seguro_facultativo.html')            
            #titular= Titular.objects.get(pk=id, safs__in=usuario.profile.safs.all())    
            titular= Titular.objects.get(pk=id)    
            beneficiarios = Beneficiario.objects.filter(titular=titular, seguro_facultativo=True)
            
            context = {'titular':titular, 
                       'usuario':usuario,
                       'fecha_actual':fecha_actual,                     
                       'beneficiarios':beneficiarios,
                       'logo':'{}{}'.format(settings.STATIC_URL, 'assets/img/logo_horizontal.png')
                       }
            html=template.render(context)
            response = HttpResponse(content_type='application/pdf')
            #la linea siguiente: descarga directamente el pdf generado
            #response['Content-Disposition'] = 'attachment; filename="Comprobante_Seguro_Vida.pdf"'                   
            pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)     
            return response
        except:            
            pass            
        return HttpResponseRedirect(reverse_lazy('titulares'))

class pdf_seguro_conyuge(View):
    def link_callback(self, uri, rel):
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

            # make sure that file exists
        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))       
        return path
    
    def get(self, request, id, **kwargs):        
        try:        
            fecha_actual = datetime.datetime.now()
            usuario = request.user
            template = get_template('app_seguro/pdf_seguro_conyuge.html')
            #titular= Titular.objects.get(pk=id, safs__in=usuario.profile.safs.all())
            titular= Titular.objects.get(pk=id)
            beneficiarios = Beneficiario.objects.filter(titular=titular, seguro_conyuge=True)
            
            context = {'titular':titular, 
                       'usuario':usuario,
                       'fecha_actual':fecha_actual,                     
                       'beneficiarios':beneficiarios,
                       'logo':'{}{}'.format(settings.STATIC_URL, 'assets/img/logo_horizontal.png')
                       }
            html=template.render(context)
            response = HttpResponse(content_type='application/pdf')
            #la linea siguiente: descarga directamente el pdf generado
            #response['Content-Disposition'] = 'attachment; filename="Comprobante_Seguro_Vida.pdf"'                   
            pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)     
            return response
        except:            
            pass            
        return HttpResponseRedirect(reverse_lazy('titulares'))    
    
class pdf_seguro_familia(View)    :
    def link_callback(self, uri, rel):
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri
            # make sure that file exists
        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))       
        return path
    
    def get(self, request, id, **kwargs):        
        try:        
            fecha_actual = datetime.datetime.now()
            usuario = request.user
            template = get_template('app_seguro/pdf_seguro_familia.html')            
            titular= Titular.objects.get(pk=id)
            beneficiarios = Beneficiario.objects.filter(titular=titular, subsidio_proteccion_flia=True)
            
            context = {'titular':titular, 
                       'usuario':usuario,
                       'fecha_actual':fecha_actual,                     
                       'beneficiarios':beneficiarios,
                       'logo':'{}{}'.format(settings.STATIC_URL, 'assets/img/logo_horizontal.png')
                       }
            html=template.render(context)
            response = HttpResponse(content_type='application/pdf')
            #la linea siguiente: descarga directamente el pdf generado
            #response['Content-Disposition'] = 'attachment; filename="Comprobante_Seguro_Vida.pdf"'                   
            pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)     
            return response
        except:            
            pass            
        return HttpResponseRedirect(reverse_lazy('titulares'))        
    
class pdf_seguro_todos(View):
    def link_callback(self, uri, rel):
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri
            # make sure that file exists
        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))       
        return path
    
    def get(self, request, id, **kwargs):        
        try:        
            fecha_actual = datetime.datetime.now()
            usuario = request.user
            template = get_template('app_seguro/pdf_seguro_todos.html')            
            titular= Titular.objects.get(pk=id)
            beneficiarios = Beneficiario.objects.filter(titular=titular).order_by('apellido', 'nombres')
            
            context = {'titular':titular, 
                       'usuario':usuario,
                       'fecha_actual':fecha_actual,                     
                       'beneficiarios':beneficiarios,
                       'logo':'{}{}'.format(settings.STATIC_URL, 'assets/img/logo_horizontal.png')
                       }
            html=template.render(context)
            response = HttpResponse(content_type='application/pdf')
            #la linea siguiente: descarga directamente el pdf generado
            #response['Content-Disposition'] = 'attachment; filename="Comprobante_Seguro_Vida.pdf"'                   
            pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)     
            return response
        except:            
            pass            
        return HttpResponseRedirect(reverse_lazy('titulares'))        

#****************** Enviar EMail *********************************************************************
#  enviar_correo

class email_comprobante_seguro(View):
    def link_callback(self, uri, rel):
        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT
        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri
        if not os.path.isfile(path):
            raise Exception('media URI must start with %s or %s' % (sUrl, mUrl))
        return path
    
    def get(self, request, id, **kwargs):        
        try:        
            fecha_actual = datetime.datetime.now()
            usuario = request.user
            template = get_template('app_seguro/pdf_seguro_todos.html')            
            titular = Titular.objects.get(pk=id)
            if titular.email:
                beneficiarios = Beneficiario.objects.filter(titular=titular).order_by()
                print('Encontro Titular')
                context = {
                    'titular': titular,
                    'usuario': usuario,
                    'fecha_actual': fecha_actual,
                    'beneficiarios': beneficiarios,
                    'logo': '{}{}'.format(settings.STATIC_URL, 'assets/img/logo_horizontal.png')
                }
                
                html = template.render(context)
                response = HttpResponse(content_type='application/pdf')
                pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)
            
                if pisa_status.err:
                    return HttpResponse('Error al generar el PDF', status=500)
            
                # Enviamos el correo electrónico con el PDF adjunto
                mensaje_email="La Caja de Créditos y Prestaciones Catamarca, adjunto archivo pdf detallando los Seguros Contratados.\nCordiales Saludos."
                if titular.sexo == 'Femenino':
                    membresia= "Estimada "+titular.nombre+", "+titular.apellido+"\n \n"
                else:
                    membresia= "Estimado "+titular.nombre+", "+titular.apellido+"\n \n"
                Asunto_del_correo= 'Comprobante de Seguros de Caja de Créditos y Prestaciones Catamarca'
                pie_del_correo = '\n\n\nEste mail es enviado automáticamente. Por favor, no lo respondas.\nEstás recibiendo este mensaje porque has estado en contacto con la CAJA DE CREDITOS Y PRESTACIONES CATAMARCA'
                Cuerpo_del_correo = membresia + mensaje_email + pie_del_correo      
                email = EmailMessage(Asunto_del_correo, Cuerpo_del_correo, settings.EMAIL_HOST_USER, [titular.email])

                titular_apenom= titular.nombre+"_"+titular.apellido+".pdf"
                email.attach('Comprobante_Seguro_'+titular_apenom, response.getvalue(), 'application/pdf')                
                email.send()               
                #return HttpResponse('Correo enviado con éxito.')
                messages.success(request, 'Correo enviado con éxito.')    
            else:
                messages.error(request, 'Atención: El Titular '+titular.apellido +' No tiene Registrado un EMAIL')                
        except Exception as e:
            # Manejar errores
            messages.error(request, 'Atención: Verifique su Conexion a Internet')                            
        return redirect('titulares')
    

def contacto_gmail(request):
    form_contacto= ContactoForm()
    if request.method == 'POST':
        form_contacto = ContactoForm(request.POST)
        if form_contacto.is_valid():
            nombre = request.POST['nombre']
            email = request.POST['email']
            mensaje = request.POST['mensaje']
       
        # Envía el correo electrónico
            try:
                send_mail(
                    'Contacto - Sub Gerencia de Seguros',
                    f'Nombre: {nombre}\nEmail: {email}\nMensaje: {mensaje}',
                    'tu_email@dominio.com',  # Dirección de correo electrónico del remitente
                    ['correo_destino@dominio.com'],  # Lista de destinatarios
                    fail_silently=False,
                )
                return redirect('contacto_recibido')
            except smtplib.SMTPException as e:               
                messages.error(request, f"Error al enviar el correo electrónico. {e}")               
        else:
            messages.error('Error. Por favor verifica que los datos esten correctos.')         
    return render(request, 'app_seguro/contacto.html', {'form_contacto':form_contacto})

## con sendgrid *****************************************************************
def contacto(request):
    form_contacto= ContactoForm()
    if request.method == 'POST':
        form_contacto = ContactoForm(request.POST)
        if form_contacto.is_valid():
            nombre = request.POST['nombre']
            email = request.POST['email']
            mensaje = request.POST['mensaje']
       
        # Envía el correo electrónico
            try:
                message = Mail(
                    from_email='segurostest@capresca.gob.ar',
                    to_emails='segurostest@capresca.gob.ar',
                    subject='Seguros - Contacto',
                    html_content=f'Nombre: {nombre}\nEmail: {email}\nMensaje: {mensaje}'
                )

                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                print(response.status_code, response.body, response.headers)                

                return redirect('contacto_recibido')
            except smtplib.SMTPException as e:               
                messages.error(request, f"Error al enviar el correo electrónico. {e}")               
        else:
            messages.error('Error. Por favor verifica que los datos esten correctos.')         
    return render(request, 'app_seguro/contacto.html', {'form_contacto':form_contacto})


def contacto_recibido(request):
    return render(request, 'app_seguro/contacto_recibido.html')
#------------------------------------------------------------------------------------------------
'''
def api_renaper(request):            
    cert_file_path = r'C:\Bustamantecg\pfx_test_sarh_capresca.pfx'

# Ruta donde certifi almacena sus certificados raíz de confianza
    certifi_ca_bundle = certifi.where()

# Ruta para el nuevo archivo de certificados combinados (en formato PEM)
    combined_cert_path = r'C:\Bustamantecg\combined_cert.pem'

# Combina el certificado PFX con los certificados de certifi
    os.system(f'openssl pkcs12 -in "{cert_file_path}" -clcerts -nokeys -out cert.pem -password pass:SSiZDLFURoVyHaCeHtLiVQyFt')
    os.system(f'openssl pkcs12 -in "{cert_file_path}" -cacerts -nokeys -out ca.pem -password pass:SSiZDLFURoVyHaCeHtLiVQyFt')
    os.system(f'cat cert.pem ca.pem "{certifi_ca_bundle}" > "{combined_cert_path}"')

# Configura la variable de entorno REQUESTS_CA_BUNDLE
    os.environ['REQUESTS_CA_BUNDLE'] = combined_cert_path

# Luego, realiza tu solicitud usando la biblioteca requests
    url = 'https://xroad-capresca.catamarca.gob.ar/r1/catamarca/GOB/10000104/RENAPER/LOGIN'
    data = {
        'client_secret': 'TkzBLLxwgWAUdcujv3rfa3TU71X0J8jeBciCKjKEd9yiUuwXiBC4UqJlRm63NAheThizoUNiz2fhV2Bv2hfXo3HHCsb79sNp0m9jkZ1hnUkuOCuC53w0skDZ1J9IH039',
        'client_id': 'tI5uQPMwSym3cnVYaTiZDADwlSs1XOieQw0ildCR',
        'grant_type': 'client_credentials'
    }

    headers = {
        'Accept': 'application/json',
        'X-Road-Client': 'catamarca/GOB/10000106/capresca'
    }

    response = requests.post(url, json=data, headers=headers, verify=True)
    print(response)
'''

##***********************************************************************************************************
'''
def api_renaper2(request):
    cert_file_path = r'C:\Bustamantecg\pfx_test_sarh_capresca.pfx'

# Ruta donde certifi almacena sus certificados raíz de confianza
    certifi_ca_bundle = certifi.where()

# Ruta para el nuevo archivo de certificados combinados (en formato PEM)
    combined_cert_path = r'C:\Bustamantecg\combined_cert.pem'

# Combina el certificado PFX con los certificados de certifi
    os.system(f'openssl pkcs12 -in "{cert_file_path}" -clcerts -nokeys -out cert.pem')
    os.system(f'openssl pkcs12 -in "{cert_file_path}" -cacerts -nokeys -out ca.pem')
    os.system(f'cat cert.pem ca.pem "{certifi_ca_bundle}" > "{combined_cert_path}"')

# Configura la variable de entorno REQUESTS_CA_BUNDLE
    os.environ['REQUESTS_CA_BUNDLE'] = combined_cert_path

# Luego, realiza tu solicitud usando la biblioteca requests
    import requests

    url = 'https://xroad-capresca.catamarca.gob.ar/r1/catamarca/GOB/10000104/RENAPER/LOGIN'
    data = {
        'client_secret': 'TkzBLLxwgWAUdcujv3rfa3TU71X0J8jeBciCKjKEd9yiUuwXiBC4UqJlRm63NAheThizoUNiz2fhV2Bv2hfXo3HHCsb79sNp0m9jkZ1hnUkuOCuC53w0skDZ1J9IH039',
        'client_id': 'tI5uQPMwSym3cnVYaTiZDADwlSs1XOieQw0ildCR',
        'grant_type': 'client_credentials'
    }

    headers = {
        'Accept': 'application/json',
        'X-Road-Client': 'catamarca/GOB/10000106/capresca'
    }
    response = requests.post(url, json=data, headers=headers, verify=True)
    print(response)

'''
'''
def obtner_renaper(request):
    conn = http.client.HTTPSConnection("xroad-capresca.catamarca.gob.ar")
    payload = json.dumps({
        "documento_identidad": "38203352",
        "genero": "m"
    })
    headers = {
        'X-Road-Client': 'catamarca/GOB/10000106/capresca',
        'Authorization': 'Bearer w2DHL2Sp6PerDitnJJpI9OtatpTBci',
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/r1/catamarca/GOB/10000104/RENAPER/OBTENER_DATOS_PERSONA", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
'''    