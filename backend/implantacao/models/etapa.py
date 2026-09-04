from django.db import models


class StatusEtapa(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    CONCLUIDA = 'concluida', 'Concluída'
    BLOQUEADA = 'bloqueada', 'Bloqueada'


class EtapaImplantacao(models.Model):
    implantacao = models.ForeignKey(
        'implantacao.Implantacao',
        related_name='etapas',
        on_delete=models.CASCADE,
    )
    nome = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField()
    status = models.CharField(
        max_length=30,
        choices=StatusEtapa.choices,
        default=StatusEtapa.PENDENTE,
    )
    obrigatoria = models.BooleanField(default=True)
    iniciada_em = models.DateTimeField(null=True, blank=True)
    concluida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'implantacoes_etapas'
        ordering = ['ordem']
        constraints = [
            models.UniqueConstraint(
                fields=['implantacao', 'ordem'],
                name='unique_implantacao_etapa_ordem',
            )
        ]

    def __str__(self):
        return f'{self.implantacao} - {self.nome}'
