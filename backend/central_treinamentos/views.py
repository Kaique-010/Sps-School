from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Modulo, Treinamento, ProgressoTreinamento
from .serializers import (
    ModuloSerializer,
    TreinamentoSerializer,
    ProgressoTreinamentoSerializer,
)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from urllib.parse import urlparse, parse_qs
import re


class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer


class TreinamentoViewSet(viewsets.ModelViewSet):
    queryset = Treinamento.objects.all()
    serializer_class = TreinamentoSerializer

    def get_queryset(self):
        """
        🔹 Permite filtrar treinamentos por módulo via query param (?modulo=ID)
        """
        modulo_id = self.request.query_params.get("modulo")
        qs = Treinamento.objects.all()
        if modulo_id:
            qs = qs.filter(modulo_id=modulo_id)
        return qs


class ProgressoTreinamentoViewSet(viewsets.ModelViewSet):
    """
    🔹 CRUD completo de progresso por usuário autenticado.
    🔹 Cria ou atualiza automaticamente o progresso (idempotente).
    """

    serializer_class = ProgressoTreinamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        🔹 Cada usuário só vê seus próprios progressos.
        """
        return ProgressoTreinamento.objects.filter(usuario=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        🔹 Cria ou atualiza o progresso do vídeo.
        🔹 Retorna o estado atualizado do progresso.
        """
        user = request.user
        dados = request.data
        treino_id = dados.get("treinamento")

        if not treino_id:
            return Response(
                {"erro": "Campo 'treinamento' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 🔹 Cria ou atualiza o progresso
        progresso, _ = ProgressoTreinamento.objects.get_or_create(
            usuario=user, treinamento_id=treino_id
        )

        # Atualiza campos recebidos
        progresso.lido = dados.get("lido", progresso.lido)
        progresso.progresso_video = dados.get(
            "progresso_video", progresso.progresso_video
        )
        progresso.save()

        return Response(
            ProgressoTreinamentoSerializer(progresso).data,
            status=status.HTTP_200_OK,
        )

    def partial_update(self, request, *args, **kwargs):
        """
        🔹 Permite PATCH para atualizar progresso incrementalmente.
        """
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ==========================
# Páginas HTML (Templates)
# ==========================

@login_required
def treinamentos_page(request, modulo_id):
    """
    Página HTML que lista os treinamentos de um módulo específico.
    """
    modulo = get_object_or_404(
        Modulo.objects.prefetch_related('treinamentos'), id=modulo_id
    )
    treinamentos = modulo.treinamentos.all()

    context = {
        'modulo': modulo,
        'treinamentos': treinamentos,
    }
    return render(request, 'treinamentos.html', context)


@login_required
def video_page(request, treinamento_id):
    """
    Página HTML para exibir o vídeo de um treinamento específico.
    """
    treinamento = get_object_or_404(Treinamento, id=treinamento_id)
    raw_url = treinamento.video_url or ""

    def build_embed(url: str):
        if not url:
            return {"type": "none", "url": None}

        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path
        qs = parse_qs(parsed.query)

        # YouTube variants
        if "youtube.com" in netloc or "youtu.be" in netloc:
            video_id = None
            if "youtu.be" in netloc:
                m = re.match(r"^/(.+)$", path)
                if m:
                    video_id = m.group(1)
            elif "/watch" in path:
                video_id = qs.get("v", [None])[0]
            elif "/embed/" in path:
                video_id = path.split("/embed/")[-1]
            elif "/shorts/" in path:
                video_id = path.split("/shorts/")[-1]

            if video_id:
                start = qs.get("t", [None])[0] or qs.get("start", [None])[0]
                start_param = f"?start={start}" if start else ""
                return {
                    "type": "youtube",
                    "url": f"https://www.youtube.com/embed/{video_id}{start_param}",
                }

        # Vimeo
        if "vimeo.com" in netloc:
            m = re.match(r"^/(\d+)", path)
            if m:
                return {
                    "type": "vimeo",
                    "url": f"https://player.vimeo.com/video/{m.group(1)}",
                }

        # Direct HTML5 video files
        if re.search(r"\.(mp4|webm|ogg)$", url, re.IGNORECASE):
            return {"type": "file", "url": url}

        # Fallback: return original URL (may still work if already embed)
        return {"type": "unknown", "url": url}

    embed = build_embed(raw_url)
    context = {
        'treinamento': treinamento,
        'video_url': raw_url,
        'embed_type': embed.get('type'),
        'embed_url': embed.get('url'),
        'conteudo': treinamento.conteudo,
    }
    return render(request, 'video.html', context)
