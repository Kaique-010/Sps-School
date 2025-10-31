from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView,
    PerfilUsuarioView,
    LogoutView,
    VerificarTokenView
)

app_name = 'autenticacao'

urlpatterns = [
    # Autenticação
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verificar-token/', VerificarTokenView.as_view(), name='verificar_token'),
    
    # Perfil do usuário
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil_usuario'),
]