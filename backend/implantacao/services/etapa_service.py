from django.db import transaction

from implantacao.models.etapa import EtapaImplantacao, StatusEtapa
from implantacao.models.tarefa import TarefaImplantacao
from implantacao.templates.etapas import ETAPAS


class EtapaService:

    @staticmethod
    @transaction.atomic
    def criar_etapas(implantacao, etapas):
        """
        Cria as etapas e respectivas tarefas de uma implantação
        a partir das definições do template.

        Parameters:
            implantacao (Implantacao): A implantação a ser associada.
            etapas (list): Lista de códigos de etapas a serem criadas.

        Returns:
            list: Lista de objetos Etapa criados.

        Raises:
            ValueError: Se um código de etapa inválido for fornecido.

        Notes:
            Todas as etapas são criadas inicialmente como PENDENTES.
            O início da implantação é responsabilidade do
            ImplantacaoService.
        """

        etapas_resolvidas = []

        for codigo in etapas:
            config = ETAPAS.get(codigo)

            if config is None:
                raise ValueError(
                    f"Etapa não encontrada no catálogo: {codigo}"
                )

            etapas_resolvidas.append(
                (codigo, config)
            )

        # Garante que a ordem do template não interfira
        # na ordem real das etapas.
        etapas_resolvidas.sort(
            key=lambda item: item[1]["ordem"]
        )

        resultado = []

        for codigo, config in etapas_resolvidas:

            etapa = EtapaImplantacao.objects.create(
                implantacao=implantacao,
                nome=config["nome"],
                ordem=config["ordem"],
                obrigatoria=config.get("obrigatoria", True),
                status=StatusEtapa.PENDENTE,
            )

            tarefas = config.get("tarefas", [])

            for tarefa_config in tarefas:
                TarefaImplantacao.objects.create(
                    etapa=etapa,
                    titulo=tarefa_config["titulo"],
                    descricao=tarefa_config.get("descricao", ""),
                    obrigatoria=tarefa_config.get(
                        "obrigatoria",
                        True,
                    ),
                )

            resultado.append(etapa)

        return resultado

    @staticmethod
    def iniciar(etapa):
        """
        Inicia uma etapa pendente.
        """

        if etapa.status == StatusEtapa.CONCLUIDA:
            raise ValueError(
                "Não é possível iniciar uma etapa concluída."
            )

        if etapa.status == StatusEtapa.BLOQUEADA:
            raise ValueError(
                "Não é possível iniciar uma etapa bloqueada."
            )

        from django.utils import timezone

        etapa.status = StatusEtapa.EM_ANDAMENTO

        if etapa.iniciada_em is None:
            etapa.iniciada_em = timezone.now()

        etapa.save(
            update_fields=[
                "status",
                "iniciada_em",
            ]
        )

        return etapa

    @staticmethod
    @transaction.atomic
    def concluir(etapa):
        """
        Conclui uma etapa após validar suas tarefas obrigatórias.
        """

        from django.utils import timezone

        tarefas_pendentes = etapa.tarefas.filter(
            obrigatoria=True,
            concluida=False,
        )

        if tarefas_pendentes.exists():
            raise ValueError(
                "Não é possível concluir a etapa. "
                "Existem tarefas obrigatórias pendentes."
            )

        etapa.status = StatusEtapa.CONCLUIDA
        etapa.concluida_em = timezone.now()

        etapa.save(
            update_fields=[
                "status",
                "concluida_em",
            ]
        )

        return etapa

    @staticmethod
    def obter_proxima(etapa):
        """
        Retorna a próxima etapa da implantação.
        """

        return (
            EtapaImplantacao.objects
            .filter(
                implantacao=etapa.implantacao,
                ordem__gt=etapa.ordem,
            )
            .order_by("ordem")
            .first()
        )

    @staticmethod
    @transaction.atomic
    def concluir_e_avancar(etapa):
        """
        Conclui a etapa atual e inicia a próxima etapa.
        """

        etapa = EtapaService.concluir(etapa)

        proxima = EtapaService.obter_proxima(etapa)

        if proxima is not None:
            EtapaService.iniciar(proxima)

        return etapa, proxima