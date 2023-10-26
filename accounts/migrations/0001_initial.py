# Generated by Django 4.2.3 on 2023-09-08 13:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_seguro', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cuil', models.CharField(help_text='sin guiones', max_length=11, unique=True)),
                ('image', models.ImageField(blank=True, default='media/user/user_defecto.png', null=True, upload_to='media/user/', verbose_name='Imagen de Perfil')),
                ('addres', models.CharField(blank=True, max_length=150, null=True, verbose_name='dirección')),
                ('location', models.CharField(blank=True, max_length=100, null=True, verbose_name='Localidad')),
                ('telephone', models.CharField(blank=True, max_length=50, null=True, verbose_name='Teléfono')),
                ('safs', models.ManyToManyField(default=1, to='app_seguro.saf', verbose_name='S.A.F.')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'perfil',
                'verbose_name_plural': 'perfiles',
                'ordering': ['-id'],
            },
        ),
    ]
