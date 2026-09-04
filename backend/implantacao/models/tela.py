from django.db import models


class StatusTela(models.TextChoices):
    PENDENTE = 'pendente', 'Pendente'
    EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
    CONCLUIDA = 'concluida', 'Concluída'


class Tela(models.Model):
    modulo = models.ForeignKey(
        'implantacao.Modulo',
        related_name='telas',
        on_delete=models.PROTECT,
    )
    codigo = models.CharField(max_length=50)
    nome = models.CharField(max_length=150)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'telas'
        constraints = [
            models.UniqueConstraint(
                fields=['modulo', 'codigo'],
                name='unique_tela_modulo_codigo',
            )
        ]
        ordering = ['modulo__nome', 'nome']

    def __str__(self):
        return self.nome


class ImplantacaoTela(models.Model):
    implantacao_modulo = models.ForeignKey(
        'implantacao.ImplantacaoModulo',
        related_name='telas',
        on_delete=models.CASCADE,
    )
    tela = models.ForeignKey(
        Tela,
        related_name='implantacoes',
        on_delete=models.PROTECT,
    )
    status = models.CharField(
        max_length=30,
        choices=StatusTela.choices,
        default=StatusTela.PENDENTE,
    )
    concluida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'implantacoes_telas'
        constraints = [
            models.UniqueConstraint(
                fields=['implantacao_modulo', 'tela'],
                name='unique_implantacao_tela',
            )
        ]
