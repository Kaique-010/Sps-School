from django.db import transaction
from django.utils import timezone

from implantacao.models.modulo import Modulo
from implantacao.models.treinamento import Treinamento
from implantacao.templates.treinamentos import TREINAMENTOS


class TreinamentoService:

    @staticmethod
    @transaction.atomic
    def criar_treinamentos(implantacao, treinamentos):
        """
        Cria os treinamentos definidos pelo template.

        A data de agendamento não é definida pelo template.
        Ela será definida posteriormente pelo processo da implantação.
        """

        resultado = []

        for codigo in treinamentos:

            config = TREINAMENTOS.get(codigo)

            if config is None:
                raise ValueError(
                    f"Treinamento não encontrado no catálogo: {codigo}"
                )

            modulo = None

            modulo_codigo = config.get("modulo")

            if modulo_codigo:
                modulo = Modulo.objects.filter(
                    codigo=modulo_codigo,
                    ativo=True,
                ).first()

                if modulo is None:
                    raise ValueError(
                        f"Módulo '{modulo_codigo}' "
                        f"não encontrado para o treinamento "
                        f"'{codigo}'."
                    )

            treinamento = Treinamento.objects.create(
                implantacao=implantacao,
                modulo=modulo,
                titulo=config["titulo"],
                descricao=config.get("descricao", ""),
                data_agendada=timezone.now(),
            )

            resultado.append(treinamento)

        return resultado

    @staticmethod
    @transaction.atomic
    def criar_agenda_padrao(implantacao):
        """Cria uma agenda padrão de treinamentos baseada nos módulos já
        associados à implantação. Fallback para treinamentos iniciais/vendas."""
        from implantacao.templates.treinamentos import TREINAMENTOS
        existentes = set(
            implantacao.treinamentos.values_list('titulo', flat=True)
        ) if implantacao.pk else set()
        agenda_padrao = []
        for codigo in ('inicial', 'vendas', 'basico'):
            if codigo in TREINAMENTOS:
                agenda_padrao.append(codigo)
        for im in implantacao.modulos_implantacao.select_related('modulo').all():
            modulo_codigo = im.modulo.codigo if im.modulo else ''
            if modulo_codigo in TREINAMENTOS:
                agenda_padrao.append(modulo_codigo)
        unicos = []
        for c in agenda_padrao:
            if c not in unicos:
                unicos.append(c)
        codigos_criar = [
            c for c in unicos
            if c in TREINAMENTOS and TREINAMENTOS[c]['titulo'] not in existentes
        ]
        if not codigos_criar:
            return []
        return TreinamentoService.criar_treinamentos(implantacao, codigos_criar)

    @staticmethod
    @transaction.atomic
    def realizar(treinamento, responsavel=None):
        """
        Marca um treinamento como realizado.
        """

        if treinamento.realizado:
            return treinamento

        treinamento.realizado = True
        treinamento.data_realizacao = timezone.now()

        if responsavel:
            treinamento.responsavel = responsavel.strip()[:120]

        treinamento.save(
            update_fields=[
                "realizado",
                "data_realizacao",
                "responsavel",
            ]
        )

        return treinamento