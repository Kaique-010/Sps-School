from django.contrib import admin
from .models import Modulo, Treinamento, ProgressoTreinamento, PerguntaTreinamento

@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'descricao')
    search_fields = ('nome', 'descricao')
    ordering = ('id',)

@admin.register(Treinamento)
class TreinamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'titulo', 'modulo', 'video_url')
    list_filter = ('modulo',)
    search_fields = ('titulo', 'conteudo')
    ordering = ('id',)

@admin.register(ProgressoTreinamento)
class ProgressoTreinamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'treinamento', 'lido', 'progresso_video', 'atualizado_em')
    list_filter = ('usuario', 'treinamento', 'lido')
    search_fields = ('usuario__username', 'treinamento__titulo')
    ordering = ('id',)

@admin.register(PerguntaTreinamento)
class PerguntaTreinamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'treinamento', 'ordem', 'texto', 'opcao_a', 'opcao_b', 'opcao_c', 'opcao_d', 'correta')
    list_filter = ('treinamento',)
    search_fields = ('treinamento__titulo', 'texto')
    ordering = ('id',)