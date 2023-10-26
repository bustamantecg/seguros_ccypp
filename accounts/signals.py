# archivo que se ejecuta cuando recibe la grabacion de un User
# es asignar automaticamente a un grupo automaticamente

from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Profile


#funcion que agrega un usuario a un grupo
@receiver(post_save, sender= Profile)
def add_user_to_students_group(sender, instance, created, **kwargs):
    if created:
        try:
            students = Group.objects.get(name='asegurados')
        except Group.DoesNotExist:
            students= Group.objects.create(name= 'asegurados')
        instance.user.groups.add(students)






