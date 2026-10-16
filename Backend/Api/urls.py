from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import (
    RegisterView,
    UsuarioViewSet,
    MensagemViewSet,
    ConversaViewSet,
    ModeloIAViewSet,
    teste,
    LoginView,
    google_login_redirect,
    ChatbotView,
)

# Router principal
router = DefaultRouter()

router.register(r'usuario', UsuarioViewSet)
router.register(r'mensagem', MensagemViewSet)
router.register(r'conversa', ConversaViewSet)
router.register(r'modeloAI', ModeloIAViewSet)

# URLs
urlpatterns = [
    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Login
    path('login/', LoginView.as_view(), name='login'),
    

    # Redirecionamento pós-login do Google (gera o JWT e manda pro front)
    path('social-redirect/', google_login_redirect, name='social_redirect'),

    # Registro
    path('auth/register/', RegisterView.as_view()),  

    # Perfil protegido
    path('teste/', teste, name='teste'),
    path('chatbot/', ChatbotView.as_view(), name='chatbot'),

    # Rotas automáticas do router
    path('', include(router.urls)),
]