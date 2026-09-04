from django.db import models


class StatusImplantacao(models.TextChoices):
    NAO_INICIADO = 'nao_iniciado', 'Não Iniciado'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    FINALIZADO = 'finalizado', 'Finalizado'
    CANCELADO = 'cancelado', 'Cancelado'


class Implantacao(models.Model):

    empresa = models.IntegerField(default=0)
    filial = models.IntegerField(default=0)
    codigo_cliente = models.CharField(max_length=50)
    cliente = models.CharField(max_length=120)
    documento_cliente = models.CharField(max_length=30)

    implantador = models.CharField(max_length=120, blank=True, default='')

    data_implantacao = models.DateField(
        null=True,
        blank=True,
    )

    prazo_implementacao = models.DateField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=30,
        choices=StatusImplantacao.choices,
        default=StatusImplantacao.NAO_INICIADO,
    )

    observacoes = models.TextField(blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'implantacoes'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.codigo_cliente} - {self.cliente}'
