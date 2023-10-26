from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from app_seguro.models import Saf


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Usuario')    
    cuil = models.CharField(max_length=11, help_text='sin guiones', unique=True)
    image = models.ImageField(default='media/user/user_defecto.png', upload_to='media/user/', verbose_name='Imagen de Perfil', null=True, blank=True)
    addres = models.CharField(max_length=150, null=True, blank=True, verbose_name='dirección')
    location = models.CharField(max_length=100, null=True, blank=True, verbose_name='Localidad')
    telephone = models.CharField(max_length=50, null=True, blank=True, verbose_name='Teléfono')        
    #safs = models.ForeignKey(Saf, on_delete=models.PROTECT, verbose_name='S.A.F.', default=1)
    safs = models.ManyToManyField(Saf, verbose_name='S.A.F.', default=1)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfiles'
        ordering = ['-id']

    def __str__(self):        
        return self.user.username
    
# esto es para cuando creo un usuario tambien crea el perfil
def create_user_profile(sender, instance, created, **kwargs) :
    if created:
        Profile.objects.create(user=instance)

# funcion que cuando graba el perfil se graba en la BD
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# con estos eventos logro conectar el usuario con el perfil
post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)


