from django.db import models
from django.contrib.auth.models import User

class Modulo(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome


class Treinamento(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='treinamentos')
    titulo = models.CharField(max_length=150)
    conteudo = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.titulo


class PerguntaTreinamento(models.Model):
    treinamento = models.ForeignKey(Treinamento, on_delete=models.CASCADE, related_name='perguntas')
    ordem = models.PositiveIntegerField(default=1)
    texto = models.CharField(max_length=255)
    opcao_a = models.CharField(max_length=255)
    opcao_b = models.CharField(max_length=255)
    opcao_c = models.CharField(max_length=255)
    opcao_d = models.CharField(max_length=255)
    correta = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])

    class Meta:
        unique_together = ('treinamento', 'ordem')

    def __str__(self):
        return f"{self.treinamento.titulo} - {self.ordem}"


class ProgressoTreinamento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    treinamento = models.ForeignKey(Treinamento, on_delete=models.CASCADE)
    lido = models.BooleanField(default=False)
    progresso_video = models.FloatField(default=0.0)  # 0–100 (%)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'treinamento')
