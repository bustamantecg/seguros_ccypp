from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static 
from django.conf import settings

urlpatterns = [
    path('accounts/', include('accounts.urls')),
    path('', include('app_seguro.urls')),
    path('Timpa/', admin.site.urls),    
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)