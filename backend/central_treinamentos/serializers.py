from rest_framework import serializers
from .models import Modulo, Treinamento, ProgressoTreinamento, PerguntaTreinamento

class TreinamentoSerializer(serializers.ModelSerializer):
    perguntas = serializers.SerializerMethodField()
    class Meta:
        model = Treinamento
        fields = '__all__'

    def get_perguntas(self, obj):
        qs = obj.perguntas.order_by('ordem')
        return PerguntaTreinamentoSerializer(qs, many=True).data


class ModuloSerializer(serializers.ModelSerializer):
    treinamentos = TreinamentoSerializer(many=True, read_only=True)
    class Meta:
        model = Modulo
        fields = ['id', 'nome', 'descricao', 'treinamentos']


class ProgressoTreinamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressoTreinamento
        fields = '__all__'
        extra_kwargs = {
            'lido': {'read_only': True}
        }


class PerguntaTreinamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerguntaTreinamento
        fields = ['id', 'ordem', 'texto', 'opcao_a', 'opcao_b', 'opcao_c', 'opcao_d']
