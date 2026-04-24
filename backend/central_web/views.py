from urllib.parse import urlparse, parse_qs
import re

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Modulo, Treinamento
from .serializers import ModuloSerializer, TreinamentoSerializer


class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all().order_by("id")
    serializer_class = ModuloSerializer
    permission_classes = [AllowAny]


class TreinamentoViewSet(viewsets.ModelViewSet):
    queryset = Treinamento.objects.all().order_by("id")
    serializer_class = TreinamentoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["modulo"]
    search_fields = ["titulo", "conteudo"]

    def get_queryset(self):
        qs = Treinamento.objects.select_related("modulo", "usuario_criador").all()

        modulo_id = self.request.query_params.get("modulo")
        if modulo_id:
            qs = qs.filter(modulo_id=modulo_id)

        return qs.order_by("id")


@login_required
def treinamentos_web(request, modulo_id):
    modulo = get_object_or_404(
        Modulo.objects.prefetch_related("treinamentos"),
        id=modulo_id,
    )

    treinamentos = modulo.treinamentos.all().order_by("id")

    context = {
        "modulo": modulo,
        "treinamentos": treinamentos,
    }

    return render(request, "treinamentos.html", context)


@login_required
def video_web(request, treinamento_id):
    treinamento = get_object_or_404(
        Treinamento.objects.select_related("modulo", "usuario_criador"),
        id=treinamento_id,
    )

    raw_url = treinamento.video or ""

    def build_embed(url: str):
        if not url:
            return {"type": "none", "url": None}

        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path
        qs = parse_qs(parsed.query)

        if "youtube.com" in netloc or "youtu.be" in netloc:
            video_id = None

            if "youtu.be" in netloc:
                match = re.match(r"^/([^/?]+)", path)
                if match:
                    video_id = match.group(1)

            elif "/watch" in path:
                video_id = qs.get("v", [None])[0]

            elif "/embed/" in path:
                video_id = path.split("/embed/")[-1].split("?")[0]

            elif "/shorts/" in path:
                video_id = path.split("/shorts/")[-1].split("?")[0]

            if video_id:
                start = qs.get("t", [None])[0] or qs.get("start", [None])[0]

                query = "?enablejsapi=1&controls=0&disablekb=1"
                if start:
                    query += f"&start={start}"

                return {
                    "type": "youtube",
                    "url": f"https://www.youtube.com/embed/{video_id}{query}",
                }

        if "vimeo.com" in netloc:
            match = re.match(r"^/(\d+)", path)
            if match:
                return {
                    "type": "vimeo",
                    "url": f"https://player.vimeo.com/video/{match.group(1)}",
                }

        if re.search(r"\.(mp4|webm|ogg)$", url, re.IGNORECASE):
            return {"type": "file", "url": url}

        return {"type": "unknown", "url": url}

    embed = build_embed(raw_url)

    context = {
        "treinamento": treinamento,
        "video_url": raw_url,
        "embed_type": embed.get("type"),
        "embed_url": embed.get("url"),
        "conteudo": treinamento.conteudo,
    }

    return render(request, "video.html", context)