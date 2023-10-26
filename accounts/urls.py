from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns= [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
 
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('reset_password/', views.CustomPasswordResetView.as_view(template_name='registration/password_reset_form2.html'), name='reset_password'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset/error/', views.CustomPasswordResetErrorView.as_view(), name='password_reset_error'),
    
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),       
]