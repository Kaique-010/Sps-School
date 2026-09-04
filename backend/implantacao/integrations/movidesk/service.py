from django.db import transaction

from implantacao.integrations.movidesk.client import MovideskClient
from implantacao.integrations.movidesk.mapper import MovideskMapper
from implantacao.models import Implantacao, OrigemMovidesk
from implantacao.services.implantacao_service import (
    ImplantacaoService,
    ModuloService,
    TreinamentoService,
)
from implantacao.services.workflow_service import WorkflowService


class MovideskImportService:
    def __init__(self, client=None):
        self.client = client or MovideskClient()

    @transaction.atomic
    def importar_ticket(self, ticket_id: int, auto_iniciar_se_implantador: bool = True):
        ticket = self.client.obter_ticket(ticket_id)
        mapeados = MovideskMapper.ticket_to_implantacao_data(ticket)

        origem: OrigemMovidesk | None = OrigemMovidesk.objects.filter(
            ticket_id=mapeados['ticket_id']
        ).first()

        implant_fields = {
            'empresa': mapeados['empresa'],
            'filial': mapeados['filial'],
            'codigo_cliente': mapeados['codigo_cliente'],
            'cliente': mapeados['cliente'],
            'documento_cliente': mapeados['documento_cliente'],
            'implantador': mapeados['implantador'],
            'data_implantacao': mapeados['data_implantacao'],
            'prazo_implementacao': mapeados['prazo_implementacao'],
            'observacoes': mapeados['observacoes'],
        }

        if origem is not None:
            implantacao = origem.implantacao
            for key, val in implant_fields.items():
                existing = getattr(implantacao, key)
                if key == 'observacoes':
                    if val and val != existing:
                        setattr(implantacao, key, val)
                elif val and not existing:
                    setattr(implantacao, key, val)
            implantacao.save()
        else:
            implantacao = Implantacao.objects.create(**implant_fields)

        ImplantacaoService.registrar_origem(
            implantacao, mapeados['ticket_id'], mapeados['raw']
        )

        WorkflowService.inicializar_fluxo_padrao(implantacao)

        modulos_sugeridos = mapeados.get('modulos_sugeridos') or []
        ModuloService.associar_nomes(implantacao, modulos_sugeridos)

        TreinamentoService.criar_agenda_padrao(implantacao)

        if auto_iniciar_se_implantador and implantacao.implantador and implantacao.status == 'nao_iniciado':
            ImplantacaoService.iniciar(implantacao)

        implantacao.refresh_from_db()
        return implantacao
