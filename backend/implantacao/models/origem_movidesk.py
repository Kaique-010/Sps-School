from django.db import models


class OrigemMovidesk(models.Model):
    implantacao = models.OneToOneField(
        'implantacao.Implantacao',
        related_name='movidesk',
        on_delete=models.CASCADE,
    )
    ticket_id = models.BigIntegerField(unique=True)
    sincronizado_em = models.DateTimeField(null=True, blank=True)
    dados_origem = models.JSONField(default=dict)

    class Meta:
        db_table = 'implantacoes_origens_movidesk'

    def __str__(self):
        return f'Movidesk #{self.ticket_id}'
