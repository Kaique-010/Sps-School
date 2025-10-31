from django.contrib import admin
from .models import Modulo, Treinamento, ProgressoTreinamento

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