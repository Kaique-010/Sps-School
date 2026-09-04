from django.db import models


class TarefaImplantacao(models.Model):
    etapa = models.ForeignKey(
        'implantacao.EtapaImplantacao',
        related_name='tarefas',
        on_delete=models.CASCADE,
    )
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    obrigatoria = models.BooleanField(default=True)
    concluida = models.BooleanField(default=False)
    concluida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'implantacoes_tarefas'
        ordering = ['-id']

    def __str__(self):
        return f'{self.id} - {self.titulo}'
