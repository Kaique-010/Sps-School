from rest_framework import serializers

from implantacao.models import Implantacao


class ImplantacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Implantacao
        fields = '__all__'
