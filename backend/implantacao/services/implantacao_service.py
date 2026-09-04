from django.db import transaction
from django.utils import timezone

from implantacao.models.implantacao import (
    Implantacao,
    StatusImplantacao,
)

from implantacao.models.origem_movidesk import OrigemMovidesk

from implantacao.services.template_service import (
    TemplateService,
)

from implantacao.services.etapa_service import (
    EtapaService,
)

from implantacao.services.modulo_service import (
    ModuloService,
)

from implantacao.services.treinamento_service import (
    TreinamentoService,
)


class ImplantacaoService:

    @staticmethod
    @transaction.atomic
    def criar(
        *,
        codigo_cliente,
        cliente,
        documento_cliente,
        empresa=1,
        filial=1,
        implantador="",
        data_implantacao=None,
        prazo_implementacao=None,
        observacoes="",
        template="padrao",
    ):
        template_config = TemplateService.obter(
            template
        )

        implantacao = Implantacao.objects.create(
            codigo_cliente=codigo_cliente,
            cliente=cliente,
            documento_cliente=documento_cliente,
            empresa=empresa,
            filial=filial,
            implantador=implantador,
            data_implantacao=data_implantacao,
            prazo_implementacao=prazo_implementacao,
            observacoes=observacoes,
            status=StatusImplantacao.NAO_INICIADO,
        )

        EtapaService.criar_etapas(
            implantacao,
            template_config["etapas"],
        )

        ModuloService.associar_modulos(
            implantacao,
            template_config["modulos"],
        )

        TreinamentoService.criar_treinamentos(
            implantacao,
            template_config["treinamentos"],
        )

        return implantacao

    @staticmethod
    @transaction.atomic
    def registrar_origem(implantacao, ticket_id, raw=None):
        """Registra (ou atualiza) a OrigemMovidesk associada à implantação."""
        origem, _ = OrigemMovidesk.objects.update_or_create(
            implantacao=implantacao,
            defaults={
                'ticket_id': ticket_id,
                'dados_origem': raw if isinstance(raw, dict) else {},
                'sincronizado_em': timezone.now(),
            },
        )
        return origem

    @staticmethod
    @transaction.atomic
    def iniciar(implantacao, implantador=None):
        """
        Inicia a implantação e sua primeira etapa.
        """

        if implantacao.status == StatusImplantacao.CANCELADO:
            raise ValueError(
                "Não é possível iniciar uma implantação cancelada."
            )

        if implantacao.status == StatusImplantacao.FINALIZADO:
            raise ValueError(
                "Não é possível iniciar uma implantação finalizada."
            )

        if implantador:
            implantacao.implantador = implantador

        if implantacao.data_implantacao is None:
            implantacao.data_implantacao = timezone.now().date()

        implantacao.status = StatusImplantacao.EM_ANDAMENTO

        implantacao.save(
            update_fields=[
                "status",
                "implantador",
                "data_implantacao",
                "atualizado_em",
            ]
        )

        primeira_etapa = (
            implantacao.etapas
            .order_by("ordem")
            .first()
        )

        if primeira_etapa is not None:
            EtapaService.iniciar(
                primeira_etapa
            )

        return implantacao

    @staticmethod
    @transaction.atomic
    def cancelar(
        implantacao,
        motivo="",
    ):
        """
        Cancela uma implantação.
        """

        if implantacao.status == StatusImplantacao.FINALIZADO:
            raise ValueError(
                "Não é possível cancelar uma implantação finalizada."
            )

        implantacao.status = StatusImplantacao.CANCELADO

        if motivo:
            observacao = (
                f"[Cancelamento - "
                f"{timezone.now():%d/%m/%Y %H:%M}] "
                f"{motivo}"
            )

            if implantacao.observacoes:
                implantacao.observacoes += (
                    f"\n{observacao}"
                )
            else:
                implantacao.observacoes = observacao

        implantacao.save(
            update_fields=[
                "status",
                "observacoes",
                "atualizado_em",
            ]
        )

        return implantacao

    @staticmethod
    @transaction.atomic
    def finalizar(implantacao):
        """
        Finaliza uma implantação.
        """

        if implantacao.status == StatusImplantacao.CANCELADO:
            raise ValueError(
                "Não é possível finalizar uma implantação cancelada."
            )

        implantacao.status = StatusImplantacao.FINALIZADO

        implantacao.save(
            update_fields=[
                "status",
                "atualizado_em",
            ]
        )

        return implantacao