from __future__ import annotations

from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from implantacao.models import (
    EtapaImplantacao,
    Implantacao,
    ImplantacaoModulo,
    StatusImplantacao,
    Treinamento,
)
from implantacao.services.implantacao_service import ImplantacaoService
from implantacao.services.modulo_service import ModuloService
from implantacao.services.workflow_service import WorkflowService
from implantacao.templates.etapas import ETAPAS
from implantacao.templates.implantacao import TEMPLATES

ETAPAS_PADRAO_NOMES = [e['nome'] for e in sorted(ETAPAS.values(), key=lambda x: x['ordem'])]

IMPLANTADORES_SUGESTAO = [
    'Analista Implantação 1',
    'Analista Implantação 2',
    'Consultor Sênior',
    'Tech Lead Implantação',
    'Gerente de Operações',
]


def _montar_pipeline_padrao(implantacao):
    pipeline = {}
    etapas_qs = list(
        EtapaImplantacao.objects.filter(implantacao=implantacao)
        .prefetch_related('tarefas')
        .order_by('ordem')
    )
    etapas_map = {e.nome: e for e in etapas_qs}

    andamento_visto = False
    for nome in ETAPAS_PADRAO_NOMES:
        etapa = etapas_map.get(nome)
        if etapa and etapa.status == 'concluida':
            concluida, andamento = True, False
        elif etapa and etapa.status == 'em_andamento':
            concluida, andamento = False, True
            andamento_visto = True
        elif etapa and etapa.status == 'bloqueada':
            concluida, andamento = False, False
        else:
            concluida, andamento = False, False

        total_tarefas = etapa.tarefas.count() if etapa else 0
        concluidas_tarefas = etapa.tarefas.filter(concluida=True).count() if etapa else 0
        if etapa and etapa.status == 'concluida':
            texto = f'{concluidas_tarefas}/{total_tarefas} tarefas'
        elif etapa and etapa.status == 'em_andamento':
            texto = f'{concluidas_tarefas}/{total_tarefas} tarefas'
        else:
            texto = 'Aguardando etapas anteriores'
        pipeline[nome] = {
            'concluida': concluida,
            'andamento': andamento,
            'texto': texto,
        }
    return pipeline


def _calcular_progresso_dados(implantacao, etapas_qs_list):
    etapas = sorted(etapas_qs_list or [], key=lambda e: (e.ordem, e.pk))
    total_etapas = len(etapas)
    etapas_concluidas = sum(1 for e in etapas if e.status == 'concluida')

    total_tarefas = sum(e.tarefas.count() for e in etapas)
    tarefas_concluidas = sum(
        sum(1 for t in e.tarefas.all() if t.concluida) for e in etapas
    )

    etapa_atual = 'A definir'
    for e in etapas:
        if e.status != 'concluida':
            etapa_atual = e.nome
            break

    if total_etapas:
        pct_etapas = (etapas_concluidas / total_etapas) * 60
    else:
        pct_etapas = 0
    if total_tarefas:
        pct_tarefas = (tarefas_concluidas / total_tarefas) * 40
    else:
        pct_tarefas = 0
    percentual = round(pct_etapas + pct_tarefas)

    if implantacao.status == StatusImplantacao.FINALIZADO:
        percentual = 100
        etapa_atual = 'Finalizada'
    elif implantacao.status == StatusImplantacao.NAO_INICIADO and total_etapas == 0:
        percentual = 0
        etapa_atual = 'Não iniciada'

    return {
        'implantacao': implantacao.pk,
        'percentual': percentual,
        'etapa_atual': etapa_atual,
        'etapas': {'total': total_etapas, 'concluidas': etapas_concluidas},
        'tarefas': {'total': total_tarefas, 'concluidas': tarefas_concluidas},
    }


def _calcular_progresso(implantacao):
    etapas = list(
        EtapaImplantacao.objects.filter(implantacao=implantacao)
        .prefetch_related('tarefas')
        .order_by('ordem')
    )
    return _calcular_progresso_dados(implantacao, etapas)


@method_decorator(login_required, name='dispatch')
class DashboardView(View):
    template_name = 'pages/dashboard.html'

    def get(self, request):
        stats = {
            'total': Implantacao.objects.count(),
            'nao_iniciado': Implantacao.objects.filter(status=StatusImplantacao.NAO_INICIADO).count(),
            'em_andamento': Implantacao.objects.filter(status=StatusImplantacao.EM_ANDAMENTO).count(),
            'finalizado': Implantacao.objects.filter(status=StatusImplantacao.FINALIZADO).count(),
            'cancelado': Implantacao.objects.filter(status=StatusImplantacao.CANCELADO).count(),
        }

        ultimas_qs = Implantacao.objects.select_related('movidesk').order_by('-criado_em')[:8]
        ultimas = list(ultimas_qs)

        etapas_pipeline = {}
        if ultimas:
            etapas_pipeline = _montar_pipeline_padrao(ultimas[0])
        else:
            for nome in ETAPAS_PADRAO_NOMES:
                etapas_pipeline[nome] = {
                    'concluida': False,
                    'andamento': False,
                    'texto': 'Aguardando primeira implantação',
                }

        ultimas_com_progresso = []
        if ultimas:
            etapa_map = {}
            implantacao_pks = [i.pk for i in ultimas]
            for etapa in (
                EtapaImplantacao.objects.filter(implantacao_id__in=implantacao_pks)
                .prefetch_related('tarefas')
                .order_by('ordem')
            ):
                etapa_map.setdefault(etapa.implantacao_id, []).append(etapa)

            for imp in ultimas:
                progresso = _calcular_progresso_dados(
                    imp,
                    etapa_map.get(imp.pk, []),
                )
                ultimas_com_progresso.append((imp, progresso))

        ctx = {
            'stats': stats,
            'ultimas': ultimas_com_progresso,
            'etapas_pipeline': etapas_pipeline,
        }
        return render(request, self.template_name, ctx)


@method_decorator(login_required, name='dispatch')
class ImplantacaoListView(ListView):
    template_name = 'pages/implantacao_list.html'
    context_object_name = 'object_list'
    paginate_by = 25

    def get_queryset(self):
        qs = Implantacao.objects.select_related('movidesk').order_by('-criado_em')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(cliente__icontains=q)
                | Q(codigo_cliente__icontains=q)
                | Q(documento_cliente__icontains=q)
                | Q(implantador__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['query'] = self.request.GET.get('q', '').strip()
        return ctx


@method_decorator(login_required, name='dispatch')
class ImplantacaoDetailView(DetailView):
    template_name = 'pages/implantacao_detail.html'
    context_object_name = 'object'
    queryset = Implantacao.objects.all()

    def get_queryset(self):
        return super().get_queryset().select_related('movidesk')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        imp = self.object
        ctx['progresso'] = _calcular_progresso(imp)
        ctx['movidesk'] = getattr(imp, 'movidesk', None)
        ctx['etapas'] = list(
            EtapaImplantacao.objects.filter(implantacao=imp)
            .prefetch_related('tarefas')
            .order_by('ordem')
        )
        ctx['modulos'] = list(
            ImplantacaoModulo.objects.filter(implantacao=imp)
            .select_related('modulo')
            .prefetch_related('telas', 'telas__tela')
            .order_by('modulo__nome')
        )
        ctx['treinamentos'] = list(
            Treinamento.objects.filter(implantacao=imp)
            .select_related('modulo')
            .order_by('data_agendada')
        )

        historico = list(
            Implantacao.objects.filter(implantador__isnull=False)
            .exclude(implantador='')
            .values_list('implantador', flat=True)
            .distinct()[:8]
        )
        sugestao = sorted({*IMPLANTADORES_SUGESTAO, *historico})
        if imp.implantador and imp.implantador not in sugestao:
            sugestao.insert(0, imp.implantador)
        ctx['implantadores_sugestao'] = [n for n in sugestao if n]
        return ctx


@method_decorator(login_required, name='dispatch')
class ImplantacaoIniciarView(View):
    def post(self, request, pk):
        imp = get_object_or_404(Implantacao, pk=pk)
        implantador = (request.POST.get('implantador') or '').strip()
        if not implantador:
            messages.error(request, 'Selecione ou informe o implantador antes de iniciar.')
            return redirect('implantacao_detail', pk=imp.pk)
        try:
            ImplantacaoService.iniciar(imp, implantador=implantador)
            messages.success(
                request,
                f'Implantação iniciada com {imp.implantador}.',
            )
        except Exception as exc:
            messages.error(request, f'Não foi possível iniciar a implantação: {exc}')
        return redirect('implantacao_detail', pk=imp.pk)


@method_decorator(login_required, name='dispatch')
class ImplantacaoCancelarView(View):
    def post(self, request, pk):
        imp = get_object_or_404(Implantacao, pk=pk)
        motivo = (request.POST.get('motivo') or '').strip() or 'Cancelado manualmente'
        try:
            ImplantacaoService.cancelar(imp, motivo=motivo)
            messages.success(request, 'Implantação cancelada.')
        except Exception as exc:
            messages.error(request, f'Não foi possível cancelar: {exc}')
        return redirect('implantacao_detail', pk=imp.pk)


@method_decorator(login_required, name='dispatch')
class ImplantacaoEtapaConcluirView(View):
    def post(self, request, pk, etapa_id):
        imp = get_object_or_404(Implantacao, pk=pk)
        etapa = get_object_or_404(EtapaImplantacao, pk=etapa_id, implantacao=imp)
        try:
            WorkflowService.concluir_etapa(etapa)
            messages.success(request, f'Etapa "{etapa.nome}" concluída.')
        except Exception as exc:
            messages.error(request, f'Não foi possível concluir a etapa: {exc}')
        return redirect('implantacao_detail', pk=imp.pk)


@method_decorator(login_required, name='dispatch')
class MovideskImportView(View):
    template_name = 'pages/movidesk_import.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        ticket_id = request.POST.get('ticket_id')
        try:
            ticket_id_int = int(ticket_id) if ticket_id else None
        except (TypeError, ValueError):
            messages.error(request, 'Informe um ID de ticket válido.')
            return render(request, self.template_name, {'ticket_id': ticket_id})

        if not ticket_id_int or ticket_id_int <= 0:
            messages.error(request, 'Informe um ID de ticket maior que zero.')
            return render(request, self.template_name, {'ticket_id': ticket_id})

        try:
            from implantacao.integrations.movidesk.service import MovideskImportService
            service = MovideskImportService()
            implantacao = service.importar_ticket(ticket_id_int)
            messages.success(
                request,
                f'Ticket #{ticket_id_int} importado com sucesso — Implantação #{implantacao.pk} criada/atualizada.',
            )
            return redirect('implantacao_detail', pk=implantacao.pk)
        except Exception as exc:
            messages.error(request, f'Falha ao importar ticket #{ticket_id_int}: {exc}')
            return render(request, self.template_name, {'ticket_id': ticket_id})


@login_required
def implantacao_nova(request):
    template_name = 'pages/implantacao_nova.html'
    if request.method == 'POST':
        codigo_cliente = (request.POST.get('codigo_cliente') or '').strip()
        cliente = (request.POST.get('cliente') or '').strip()
        documento_cliente = (request.POST.get('documento_cliente') or '').strip()
        empresa = request.POST.get('empresa') or 0
        filial = request.POST.get('filial') or 0
        implantador = (request.POST.get('implantador') or '').strip()
        data_implantacao = (request.POST.get('data_implantacao') or None) or None
        prazo = (request.POST.get('prazo_implementacao') or None) or None
        observacoes = (request.POST.get('observacoes') or '').strip()
        template = (request.POST.get('template') or 'padrao').strip()
        movidesk_ticket_id = (request.POST.get('movidesk_ticket_id') or '').strip() or None
        modulos_codigos_raw = (request.POST.get('modulos_codigos') or '').strip() or None

        if not codigo_cliente or not cliente or not documento_cliente:
            messages.error(request, 'Preencha os campos obrigatórios: Código, Cliente e Documento.')
            return render(request, template_name, {'form_data': request.POST, 'templates': TEMPLATES})

        try:
            imp = ImplantacaoService.criar(
                codigo_cliente=codigo_cliente,
                cliente=cliente,
                documento_cliente=documento_cliente,
                empresa=int(empresa),
                filial=int(filial),
                implantador=implantador,
                data_implantacao=data_implantacao,
                prazo_implementacao=prazo,
                observacoes=observacoes,
                template=template,
            )
            if modulos_codigos_raw:
                codigos = [c.strip() for c in modulos_codigos_raw.split(',') if c.strip()]
                if codigos:
                    ModuloService.associar_nomes(imp, codigos)
            if movidesk_ticket_id and str(movidesk_ticket_id).isdigit():
                try:
                    from implantacao.integrations.movidesk.client import MovideskClient
                    from implantacao.integrations.movidesk.mapper import MovideskMapper
                    client = MovideskClient()
                    raw = client.obter_ticket(int(movidesk_ticket_id))
                    ImplantacaoService.registrar_origem(imp, int(movidesk_ticket_id), raw)
                except Exception as e:
                    messages.warning(
                        request,
                        f'Implantação #{imp.pk} criada, porém não foi possível registrar a origem Movidesk: {e}'
                    )
            messages.success(request, f'Implantação #{imp.pk} criada com sucesso.')
            return redirect('implantacao:implantacao_detail', pk=imp.pk)
        except Exception as exc:
            messages.error(request, f'Erro ao criar implantação: {exc}')
            return render(request, template_name, {'form_data': request.POST, 'templates': TEMPLATES})

    templates_meta = {k: {'nome': v['nome'], 'modulos': list(v.get('modulos', [])),
                          'etapas': list(v.get('etapas', [])), 'treinamentos': list(v.get('treinamentos', []))}
                      for k, v in TEMPLATES.items()}
    return render(request, template_name, {'templates': TEMPLATES, 'templates_meta': templates_meta})


@login_required
def movidesk_preview_ticket(request):
    """Endpoint JSON: busca ticket por ID e retorna dados mapeados (sem salvar).
    Usado pelo formulário de Nova Implantação para pré-preencher."""
    ticket_id_raw = request.GET.get('ticket_id') or ''
    if not ticket_id_raw:
        return JsonResponse({'ok': False, 'erro': 'Informe ticket_id na query string.'}, status=400)
    try:
        ticket_id = int(ticket_id_raw)
    except (TypeError, ValueError):
        return JsonResponse({'ok': False, 'erro': 'ticket_id deve ser um número inteiro.'}, status=400)

    try:
        from implantacao.integrations.movidesk.client import MovideskClient
        from implantacao.integrations.movidesk.mapper import MovideskMapper
        client = MovideskClient()
        ticket = client.obter_ticket(ticket_id)
        data = MovideskMapper.ticket_to_implantacao_data(ticket)
        data.pop('raw', None)
        if 'data_implantacao' in data and data['data_implantacao'] is not None:
            data['data_implantacao'] = data['data_implantacao'].isoformat()
        if 'prazo_implementacao' in data and data['prazo_implementacao'] is not None:
            data['prazo_implementacao'] = data['prazo_implementacao'].isoformat()
        data['modulos_sugeridos'] = list(data.get('modulos_sugeridos') or [])
        return JsonResponse({'ok': True, 'dados': data})
    except Exception as exc:
        return JsonResponse({'ok': False, 'erro': f'{exc}'}, status=502)
