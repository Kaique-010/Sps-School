from django.contrib import admin

from .models import Modulo, Treinamento


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ("id", "nome", "descricao")
    search_fields = ("nome", "descricao")


@admin.register(Treinamento)
class TreinamentoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "empresa",
        "modulo",
        "titulo",
        "data_criacao",
        "data_atualizacao",
        "usuario_criador",
        "video",
    )
    search_fields = ("titulo", "conteudo", "video")
    list_filter = ("empresa", "modulo", "data_criacao")
    autocomplete_fields = ("modulo", "usuario_criador")