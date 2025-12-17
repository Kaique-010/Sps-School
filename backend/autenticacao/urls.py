from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView,
    PerfilUsuarioView,
    PerfilTemplateView,
    LogoutView,
    VerificarTokenView,
    SessionLoginView,
)

app_name = 'autenticacao'

urlpatterns = [
    # Autenticação JWT (API) - compatível com clientes existentes
    path('', LoginView.as_view(), name='login'),
    path('login/', LoginView.as_view(), name='login_api'),
    
    # Autenticação de sessão para templates web
    path('session-login/', SessionLoginView.as_view(), name='session_login'),

    # Logout via API
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verificar-token/', VerificarTokenView.as_view(), name='verificar_token'),
    
    # Perfil do usuário (API)
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),
    
    # Perfil do usuário (Template)
    path('meu-perfil/', PerfilTemplateView.as_view(), name='perfil_template'),
]