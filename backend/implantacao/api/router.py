from rest_framework.routers import DefaultRouter

from .views_implantacao import ImplantacaoViewSet

router = DefaultRouter()
router.register('implantacoes', ImplantacaoViewSet, basename='implantacao')
