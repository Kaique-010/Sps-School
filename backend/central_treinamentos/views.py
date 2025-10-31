from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Modulo, Treinamento, ProgressoTreinamento
from .serializers import ModuloSerializer, TreinamentoSerializer, ProgressoTreinamentoSerializer

class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer


class TreinamentoViewSet(viewsets.ModelViewSet):
    queryset = Treinamento.objects.all()
    serializer_class = TreinamentoSerializer

    def get_queryset(self):
        queryset = Treinamento.objects.all()
        modulo_id = self.request.query_params.get('modulo', None)
        if modulo_id is not None:
            queryset = queryset.filter(modulo_id=modulo_id)
        return queryset


class ProgressoTreinamentoViewSet(viewsets.ModelViewSet):
    queryset = ProgressoTreinamento.objects.all()
    serializer_class = ProgressoTreinamentoSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        dados = request.data
        treino_id = dados.get('treinamento')

        progresso, _ = ProgressoTreinamento.objects.get_or_create(
            usuario=user, treinamento_id=treino_id
        )
        progresso.lido = dados.get('lido', progresso.lido)
        progresso.progresso_video = dados.get('progresso_video', progresso.progresso_video)
        progresso.save()

        return Response(ProgressoTreinamentoSerializer(progresso).data)
