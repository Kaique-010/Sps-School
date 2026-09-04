from django.urls import path
from implantacao import views

app_name = 'implantacao'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('lista/', views.ImplantacaoListView.as_view(), name='implantacao_list'),
    path('nova/', views.implantacao_nova, name='implantacao_nova'),
    path('movidesk/preview/', views.movidesk_preview_ticket, name='movidesk_preview'),
    path('<int:pk>/', views.ImplantacaoDetailView.as_view(), name='implantacao_detail'),
    path('<int:pk>/iniciar/', views.ImplantacaoIniciarView.as_view(), name='implantacao_iniciar'),
    path('<int:pk>/cancelar/', views.ImplantacaoCancelarView.as_view(), name='implantacao_cancelar'),
    path('<int:pk>/etapa/<int:etapa_id>/concluir/', views.ImplantacaoEtapaConcluirView.as_view(), name='implantacao_etapa_concluir'),
    path('importar/movidesk/', views.MovideskImportView.as_view(), name='movidesk_import'),
]
