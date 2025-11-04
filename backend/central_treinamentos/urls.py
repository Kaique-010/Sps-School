from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    ModuloViewSet,
    TreinamentoViewSet,
    ProgressoTreinamentoViewSet,
    treinamentos_page,
    video_page,
)

router = DefaultRouter()
router.register(r'modulos', ModuloViewSet)
router.register(r'treinamentos', TreinamentoViewSet)
# Especifica basename pois o ViewSet usa get_queryset sem atributo queryset
router.register(r'progresso', ProgressoTreinamentoViewSet, basename='progresso')

urlpatterns = [
    # Páginas HTML
    path('pages/treinamentos/<int:modulo_id>/', treinamentos_page, name='treinamentos_page'),
    path('pages/video/<int:treinamento_id>/', video_page, name='video_page'),
]

# Incluir as rotas da API do router
urlpatterns += router.urls
