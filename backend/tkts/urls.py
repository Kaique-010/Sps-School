from django.urls import path
from .views import PainelAtrasadosView

app_name = 'tkts'

urlpatterns = [
    path('painel/', PainelAtrasadosView.as_view(), name='painel_atrasados'),
]
