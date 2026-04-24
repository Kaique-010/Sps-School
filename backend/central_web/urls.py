from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    ModuloViewSet,
    TreinamentoViewSet,
    treinamentos_web,
    video_web,
)

router = DefaultRouter()
router.register(r'modulos', ModuloViewSet)
router.register(r'treinamentos', TreinamentoViewSet)

urlpatterns = [
    # Páginas HTML
    path('pages/treinamentos/<int:modulo_id>/', treinamentos_web, name='treinamentos_web'),
    path('pages/video/<int:treinamento_id>/', video_web, name='video_web'),
]

# Incluir as rotas da API do router
urlpatterns += router.urls
