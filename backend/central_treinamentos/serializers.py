from rest_framework import serializers
from .models import Modulo, Treinamento, ProgressoTreinamento

class TreinamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treinamento
        fields = '__all__'


class ModuloSerializer(serializers.ModelSerializer):
    treinamentos = TreinamentoSerializer(many=True, read_only=True)
    class Meta:
        model = Modulo
        fields = ['id', 'nome', 'descricao', 'treinamentos']


class ProgressoTreinamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressoTreinamento
        fields = '__all__'
