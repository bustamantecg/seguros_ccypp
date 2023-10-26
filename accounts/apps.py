from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name='perfiles'

    def ready(self):
        import accounts.signals

# la funcion ready(), se llama cuando se carga la aplicacion y se utiliza
# para realizar cualquier iniciañlizacion o configuracion adicional
#que deba realizarse antes de que se pueda usar la aplicacion         