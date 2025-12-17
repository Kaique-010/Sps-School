from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Modulo, Treinamento, ProgressoTreinamento, PerguntaTreinamento
from .serializers import (
    ModuloSerializer,
    TreinamentoSerializer,
    ProgressoTreinamentoSerializer,
    PerguntaTreinamentoSerializer,
)
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from urllib.parse import urlparse, parse_qs
import re
from rest_framework.decorators import action
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication


class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.all()
    serializer_class = ModuloSerializer
    permission_classes = [AllowAny]


class TreinamentoViewSet(viewsets.ModelViewSet):
    queryset = Treinamento.objects.all()
    serializer_class = TreinamentoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        🔹 Permite filtrar treinamentos por módulo via query param (?modulo=ID)
        """
        modulo_id = self.request.query_params.get("modulo")
        qs = Treinamento.objects.all()
        if modulo_id:
            qs = qs.filter(modulo_id=modulo_id)
        return qs

    @action(detail=True, methods=["post"], url_path="quiz")
    def submit_quiz(self, request, pk=None):
        treinamento = self.get_object()
        respostas = request.data.get("respostas", {})
        perguntas = PerguntaTreinamento.objects.filter(treinamento=treinamento).order_by("ordem")
        total = perguntas.count()
        corretas = 0
        for p in perguntas:
            resp = respostas.get(str(p.id)) or respostas.get(p.id)
            if resp and str(resp).upper() == p.correta:
                corretas += 1
        aprovado = (total > 0 and corretas == total)
        if request.user.is_authenticated:
            prog, _ = ProgressoTreinamento.objects.get_or_create(
                usuario=request.user, treinamento=treinamento
            )
            if aprovado:
                prog.lido = True
                prog.save()
        return Response({"aprovado": aprovado, "corretas": corretas, "total": total})


class ProgressoTreinamentoViewSet(viewsets.ModelViewSet):
    """
    🔹 CRUD completo de progresso por usuário autenticado.
    🔹 Cria ou atualiza automaticamente o progresso (idempotente).
    """

    serializer_class = ProgressoTreinamentoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, JWTAuthentication]

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

        progresso, _ = ProgressoTreinamento.objects.get_or_create(
            usuario=user, treinamento_id=treino_id
        )

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
    modulo = get_object_or_404(Modulo.objects.prefetch_related('treinamentos'), id=modulo_id)
    treinamentos = modulo.treinamentos.all()
    progressos = {}
    if request.user.is_authenticated:
        qs = ProgressoTreinamento.objects.filter(usuario=request.user, treinamento__in=treinamentos)
        for p in qs:
            progressos[p.treinamento_id] = {"lido": p.lido, "progresso_video": p.progresso_video}

    context = {
        'modulo': modulo,
        'treinamentos': treinamentos,
        'progressos': progressos,
    }
    return render(request, 'treinamentos.html', context)


@login_required
def video_page(request, treinamento_id):
    """
    Página HTML para exibir o vídeo de um treinamento específico.
    """
    treinamento = get_object_or_404(Treinamento, id=treinamento_id)
    raw_url = treinamento.video_url or ""
    perguntas = PerguntaTreinamento.objects.filter(treinamento=treinamento).order_by("ordem")
    progresso_atual = None
    if request.user.is_authenticated:
        progresso_atual = ProgressoTreinamento.objects.filter(usuario=request.user, treinamento=treinamento).first()

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
                if start:
                    q = f"?start={start}&enablejsapi=1&controls=0&disablekb=1"
                else:
                    q = "?enablejsapi=1&controls=0&disablekb=1"
                return {
                    "type": "youtube",
                    "url": f"https://www.youtube.com/embed/{video_id}{q}",
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
        'perguntas': perguntas,
        'progresso_inicial': progresso_atual.progresso_video if progresso_atual else 0.0,
        'aprovado': progresso_atual.lido if progresso_atual else False,
    }
    return render(request, 'video.html', context)
