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
    path('<int:pk>/etapa/<int:etapa_id>/tarefa/<int:tarefa_id>/concluir/', views.ImplantacaoTarefaConcluirView.as_view(), name='implantacao_tarefa_concluir'),
    path('<int:pk>/modulo/<int:modulo_id>/tela/<int:tela_id>/concluir/', views.ImplantacaoTelaConcluirView.as_view(), name='implantacao_tela_concluir'),
    path('<int:pk>/modulo/<int:modulo_id>/concluir/', views.ImplantacaoModuloConcluirView.as_view(), name='implantacao_modulo_concluir'),
    path('<int:pk>/editar-treinamentos/', views.editar_treinamentos, name='editar_treinamentos'),
    path('<int:pk>/editar-modulos/', views.editar_modulos, name='editar_modulos'),
    path('<int:pk>/kickoff-form/', views.kickoff_form, name='kickoff_form'),
    path('<int:pk>/gerar-pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('<int:pk>/acao/movidesk/', views.ImplantacaoEnviarAcaoView.as_view(), name='implantacao_enviar_acao'),
    path('importar/movidesk/', views.MovideskImportView.as_view(), name='movidesk_import'),
]
