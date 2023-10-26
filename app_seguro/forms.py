from django import forms
from accounts.models import Profile
from django.contrib.auth.models import User
from django.forms import ModelForm, EmailInput, DateInput
from django.contrib.auth.forms import UserCreationForm


from .choices import *
from .models import Beneficiario, CargadorSeguro, Contacto, Titular

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['cuil','addres', 'location', 'telephone']
"""         fields = ['user','addres', 'location', 'telephone']
        widgets = {
            'user': forms.TextInput(attrs={'disabled': 'disabled'}),
        }     """

class UserForm(ModelForm):
    class Meta:
        model = User        
        fields = ['username', 'first_name', 'last_name', 'email']
        #fields = '__all__'

#-------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------

class TitularForm(ModelForm):    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   
        self.fields['fecha_nacimiento'].widget.format = '%d/%m/%Y'

    class Meta:
        model = Titular
        fields = '__all__'
        widgets = {
            'email': EmailInput(attrs={'type': 'email'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        exclude = ["usuario", "edito"]

#-------------------------------------------------------------------------------------------------------   
class BeneficiarioForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   
        self.fields['fecha_nacimiento'].widget.format = '%d/%m/%Y'

    class Meta:
        model = Beneficiario
        fields = '__all__'
        widgets = {
            'email': forms.EmailInput(attrs={'type': 'email'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),               
        }
        exclude = ["titular", 'operador']
#-------------------------------------------------------------------------------------------------------

class CargadorForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)   
        self.fields['fecha_nacimiento'].widget.format = '%d/%m/%Y'

    class Meta:
        model = CargadorSeguro
        fields = '__all__'
        widgets = {
            'email': EmailInput(attrs={'type': 'email'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

#------------------- EMail -----------------------------------------------------------------------------
class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = '__all__'
        widgets = {
            'email': EmailInput(attrs={'type': 'email'}),
        }

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
