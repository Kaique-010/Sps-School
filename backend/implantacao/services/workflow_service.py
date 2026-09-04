from django.db import transaction
from django.utils import timezone

from implantacao.models import EtapaImplantacao, Implantacao, StatusEtapa, TarefaImplantacao
from implantacao.templates.etapas import ETAPAS

ETAPAS_PADRAO = sorted(ETAPAS.values(), key=lambda x: x['ordem'])


class WorkflowService:
    @staticmethod
    @transaction.atomic
    def inicializar_fluxo_padrao(implantacao: Implantacao):
        existentes = {
            e.nome: e
            for e in EtapaImplantacao.objects.filter(implantacao=implantacao)
        }

        primeira = True
        for spec in ETAPAS_PADRAO:
            etapa = existentes.get(spec['nome'])
            status_inicial = StatusEtapa.EM_ANDAMENTO if primeira else StatusEtapa.PENDENTE

            if etapa is None:
                etapa = EtapaImplantacao.objects.create(
                    implantacao=implantacao,
                    nome=spec['nome'],
                    ordem=spec['ordem'],
                    obrigatoria=spec.get('obrigatoria', True),
                    status=status_inicial,
                    iniciada_em=timezone.now() if primeira else None,
                )

            tarefas_existentes = {
                t.titulo: t for t in etapa.tarefas.all()
            }
            for tarefa_spec in spec.get('tarefas', []):
                titulo = tarefa_spec.get('titulo')
                obrigatoria = tarefa_spec.get('obrigatoria', True)
                if titulo and titulo not in tarefas_existentes:
                    TarefaImplantacao.objects.create(
                        etapa=etapa,
                        titulo=titulo,
                        obrigatoria=obrigatoria,
                        concluida=False,
                    )

            primeira = False
        return EtapaImplantacao.objects.filter(implantacao=implantacao).order_by('ordem')

    @staticmethod
    @transaction.atomic
    def iniciar_etapa(etapa: EtapaImplantacao):
        etapa.status = StatusEtapa.EM_ANDAMENTO
        if etapa.iniciada_em is None:
            etapa.iniciada_em = timezone.now()
        etapa.save(update_fields=['status', 'iniciada_em'])
        return etapa

    @staticmethod
    @transaction.atomic
    def concluir_etapa(etapa: EtapaImplantacao):
        etapa.status = StatusEtapa.CONCLUIDA
        etapa.concluida_em = timezone.now()
        etapa.save(update_fields=['status', 'concluida_em'])

        proxima = (
            EtapaImplantacao.objects.filter(
                implantacao=etapa.implantacao,
                ordem__gt=etapa.ordem,
            )
            .order_by('ordem')
            .first()
        )
        if proxima and proxima.status == StatusEtapa.PENDENTE:
            WorkflowService.iniciar_etapa(proxima)
        return etapa
