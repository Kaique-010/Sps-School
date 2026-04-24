from rest_framework import serializers
from .models import Modulo, Treinamento



class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modulo
        fields = "__all__"


class TreinamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Treinamento
        fields = "__all__"