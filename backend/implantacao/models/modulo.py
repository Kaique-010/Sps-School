from django.db import models


class StatusModulo(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    CONCLUIDO = 'concluido', 'Concluído'


class Modulo(models.Model):
    codigo = models.CharField(max_length=30, unique=True)
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'modulos'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class ImplantacaoModulo(models.Model):
    implantacao = models.ForeignKey(
        'implantacao.Implantacao',
        related_name='modulos',
        on_delete=models.CASCADE,
    )
    modulo = models.ForeignKey(
        Modulo,
        related_name='implantacoes',
        on_delete=models.PROTECT,
    )
    status = models.CharField(
        max_length=30,
        choices=StatusModulo.choices,
        default=StatusModulo.PENDENTE,
    )
    observacoes = models.TextField(blank=True)

    class Meta:
        db_table = 'implantacoes_modulos'
        constraints = [
            models.UniqueConstraint(
                fields=['implantacao', 'modulo'],
                name='unique_implantacao_modulo',
            )
        ]

    def __str__(self):
        return f'{self.implantacao} - {self.modulo}'
