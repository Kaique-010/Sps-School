from django.contrib import admin

from .models import (
    EtapaImplantacao,
    Implantacao,
    ImplantacaoModulo,
    ImplantacaoTela,
    Modulo,
    OrigemMovidesk,
    TarefaImplantacao,
    Tela,
    Treinamento,
)

admin.site.register([
    Implantacao,
    Modulo,
    ImplantacaoModulo,
    Tela,
    ImplantacaoTela,
    EtapaImplantacao,
    TarefaImplantacao,
    Treinamento,
    OrigemMovidesk,
])
