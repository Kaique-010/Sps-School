from django.db import models
from django.conf import settings


class Modulo(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Modulo"
        verbose_name_plural = "Modulos"
        ordering = ["id"]

    def __str__(self):
        return self.nome


class Treinamento(models.Model):
    empresa = models.IntegerField(default=1)
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.PROTECT,
        related_name="treinamentos"
    )
    titulo = models.CharField(max_length=255)
    conteudo = models.TextField(blank=True, null=True)
    video = models.URLField(max_length=500, blank=True, null=True)

    data_criacao = models.DateTimeField(blank=True, null=True)
    data_atualizacao = models.DateTimeField(blank=True, null=True)

    usuario_criador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="treinamentos_criados"
    )

    class Meta:
        verbose_name = "Treinamento"
        verbose_name_plural = "Treinamentos"
        ordering = ["id"]

    def __str__(self):
        return self.titulo