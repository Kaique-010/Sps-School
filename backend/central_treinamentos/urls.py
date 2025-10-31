from rest_framework.routers import DefaultRouter
from .views import ModuloViewSet, TreinamentoViewSet, ProgressoTreinamentoViewSet

router = DefaultRouter()
router.register(r'modulos', ModuloViewSet)
router.register(r'treinamentos', TreinamentoViewSet)
router.register(r'progresso', ProgressoTreinamentoViewSet)

urlpatterns = router.urls
