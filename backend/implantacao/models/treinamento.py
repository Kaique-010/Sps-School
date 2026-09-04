from django.db import models


class Treinamento(models.Model):
    implantacao = models.ForeignKey(
        "implantacao.Implantacao",
        related_name="treinamentos",
        on_delete=models.CASCADE,
    )

    modulo = models.ForeignKey(
        "implantacao.Modulo",
        related_name="treinamentos",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    titulo = models.CharField(
        max_length=150,
    )

    descricao = models.TextField(
        blank=True,
    )

    data_agendada = models.DateTimeField(
        null=True,
        blank=True,
    )

    realizado = models.BooleanField(
        default=False,
    )

    data_realizacao = models.DateTimeField(
        null=True,
        blank=True,
    )

    responsavel = models.CharField(
        max_length=120,
        blank=True,
    )

    observacoes = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = 'implantacoes_treinamentos'
        ordering = ['-data_agendada']

    def __str__(self):
        data = self.data_agendada.strftime('%d/%m/%Y %H:%M') if self.data_agendada else 'Sem data'
        return f'{self.id} - {self.modulo or "Geral"} - {data}'
