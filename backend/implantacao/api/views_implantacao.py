from rest_framework import viewsets

from implantacao.models import Implantacao
from .serializers import ImplantacaoSerializer


class ImplantacaoViewSet(viewsets.ModelViewSet):
    queryset = Implantacao.objects.all()
    serializer_class = ImplantacaoSerializer
