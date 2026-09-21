from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from Api.views import confirmar_email

@login_required
def google_login_callback(request):
    return redirect("http://localhost:5173/login-callback")

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('dj_rest_auth.urls')),

    # Precisa vir ANTES do include('allauth.urls') para sobrescrever
    # a tela padrão de confirmação de e-mail do allauth.
    path('accounts/confirm-email/<str:key>/', confirmar_email, name='account_confirm_email'),

    path('accounts/', include('allauth.urls')),
    
    path('Api/', include('Api.urls')),

    path('register/', include('Api.urls')),

    path('accounts/profile/', google_login_callback),
]