from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any


_CNPJ_RE = re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b')
_CPF_RE = re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b')
_DOC_ONLY_RE = re.compile(r'\D')

from implantacao.templates.modulos import MODULOS


_CHAVES_MODULOS = {
    'cadastros': ['cadastro', 'entidade', 'produto', 'transportadora', 'cadastros'],
    'vendas': ['venda', 'pedido', 'orcamento', 'orçamento', 'nf', 'nota fiscal', 'vendas'],
    'financeiro_basico': ['financeiro', 'contas a pagar', 'contas a receber', 'contas pagar', 'contas receber'],
    'financeiro_robusto': ['fluxo de caixa', 'caixa', 'frente de caixa', 'financeiro completo', 'financeiro robusto'],
    'transportes': ['transporte', 'transportadoras', 'cte', 'cte', 'mdfe', 'mdfe', 'transportes'],
    'agricola': ['agricola', 'agrícola', 'agro', 'fazenda', 'safra'],
    'contabilidade': ['contabilidade', 'contabil', 'contábil', 'sped', 'escrituracao', 'escrituração'],
}

MODULOS_PADRAO = []
for codigo, cfg in MODULOS.items():
    chaves = _CHAVES_MODULOS.get(codigo, [codigo.lower(), cfg['nome'].lower()])
    MODULOS_PADRAO.append({'nome': codigo, 'chaves': tuple(chaves)})

DETECTAR_FALLBACK = ['cadastros', 'vendas', 'financeiro_basico']


class MovideskFormatter:
    @staticmethod
    def format_document(doc: str) -> str:
        d = _DOC_ONLY_RE.sub('', doc or '')
        if len(d) == 14:
            return f'{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}'
        if len(d) == 11:
            return f'{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}'
        return d


class MovideskMapper:
    """Converte payload do Movidesk para o domínio Implantação.

    Estratégia defensiva: o ticket real do Movidesk tem campos variáveis por
    customização do cliente. Extraímos com falha segura para não quebrar o
    import e gravamos o payload bruto em OrigemMovidesk.dados_origem.
    """

    @staticmethod
    def ticket_to_implantacao_data(ticket: dict) -> dict:
        ticket = ticket or {}

        ticket_id = MovideskMapper._extract_ticket_id(ticket)
        customer = ticket.get('customer') or {}
        clients = ticket.get('clients') or []
        owner = ticket.get('owner') or ticket.get('ownerTeam') or {}
        created_by = ticket.get('createdBy') or {}

        codigo_cliente = (
            str(customer.get('id') or '').strip()
            or str(ticket.get('organizationId') or '').strip()
            or (str(ticket_id) if ticket_id else '')
        )
        cliente = (
            str(customer.get('businessName') or customer.get('name') or '').strip()
            or MovideskMapper._pick_client_name(clients)
            or f'Ticket {ticket_id}'
        )
        documento = MovideskMapper._extract_document(customer, clients, ticket)

        implantador = MovideskMapper._extract_owner_name(owner) or MovideskMapper._extract_owner_name(created_by) or ''

        data_implantacao = MovideskMapper._parse_date(
            ticket.get('createdDate') or ticket.get('openedDate') or ticket.get('openDate')
        )
        prazo = MovideskMapper._parse_date(
            ticket.get('slaSolutionDate') or ticket.get('solutionDate') or ticket.get('dueDate')
        )
        if prazo is None and data_implantacao is not None:
            prazo = data_implantacao + timedelta(days=20)

        assunto = str(ticket.get('subject') or ticket.get('description') or '').strip()
        observacoes = []
        if assunto:
            observacoes.append(f'Assunto Movidesk: {assunto[:300]}')
        protocolo = str(ticket.get('number') or ticket.get('protocol') or '').strip()
        if protocolo:
            observacoes.append(f'Protocolo Movidesk: {protocolo}')
        if clients:
            contatos = [
                f"{c.get('businessName') or c.get('name') or ''} <{c.get('email') or ''}>".strip(' <>:,')
                for c in clients[:3]
                if c.get('businessName') or c.get('name') or c.get('email')
            ]
            if contatos:
                observacoes.append('Contatos: ' + '; '.join(contatos))

        modulos_sugeridos = MovideskMapper._detectar_modulos(ticket)
        template_sugerido = MovideskMapper._sugerir_template(modulos_sugeridos)

        return {
            'ticket_id': ticket_id,
            'codigo_cliente': codigo_cliente[:50],
            'empresa': 1,
            'filial': 1,
            'cliente': cliente[:120],
            'documento_cliente': documento[:30],
            'implantador': implantador[:120],
            'data_implantacao': data_implantacao,
            'prazo_implementacao': prazo,
            'observacoes': '\n'.join(filter(None, observacoes)),
            'modulos_sugeridos': modulos_sugeridos,
            'template_sugerido': template_sugerido,
            'protocol': protocolo,
            'raw': ticket,
        }

    @staticmethod
    def _extract_ticket_id(ticket: dict) -> int | None:
        for key in ('id', 'ticketId', 'ticket_id', 'number'):
            try:
                v = ticket.get(key)
                if v is not None and str(v).isdigit():
                    return int(v)
            except (TypeError, ValueError):
                continue
        return None

    @staticmethod
    def _pick_client_name(clients: list[dict]) -> str:
        for c in clients:
            nome = str(c.get('businessName') or c.get('name') or '').strip()
            if nome:
                return nome
        return ''

    @staticmethod
    def _extract_document(customer: dict, clients: list[dict], ticket: dict) -> str:
        sources: list[Any] = [customer] + list(clients or [])
        for src in sources:
            for key in ('cnpj', 'cpf', 'federalId', 'federal_id', 'document', 'documentNumber', 'inscricao_federal'):
                val = str(src.get(key) or '').strip()
                cleaned = _DOC_ONLY_RE.sub('', val)
                if cleaned and len(cleaned) in (11, 14):
                    return MovideskFormatter.format_document(cleaned)

        haystack = ' '.join(filter(None, [
            str(customer.get('businessName') or ''),
            str(customer.get('name') or ''),
            str(ticket.get('subject') or ''),
            str(ticket.get('description') or ''),
            ' '.join(str(c.get('businessName') or c.get('name') or c.get('email') or '') for c in clients),
        ]))
        for regex in (_CNPJ_RE, _CPF_RE):
            m = regex.search(haystack)
            if m:
                return m.group(0)
        return ''

    @staticmethod
    def _extract_owner_name(owner: dict) -> str:
        if not owner:
            return ''
        parts = [owner.get('businessName'), owner.get('name'), owner.get('nickname')]
        for p in parts:
            v = str(p or '').strip()
            if v:
                return v
        if isinstance(owner.get('id'), (str, int)) and str(owner['id']):
            pessoa = owner.get('person') or {}
            v = str(pessoa.get('businessName') or pessoa.get('name') or '').strip()
            if v:
                return v
        return ''

    @staticmethod
    def _parse_date(value: Any):
        if not value:
            return None
        if isinstance(value, datetime):
            return value.date()
        if hasattr(value, 'date'):
            try:
                return value.date()
            except Exception:
                return None
        raw = str(value).strip()
        if not raw:
            return None
        fmts = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d/%m/%Y %H:%M:%S',
        ]
        for fmt in fmts:
            try:
                return datetime.strptime(raw[: len(fmt) + 4], fmt).date()
            except (ValueError, TypeError):
                continue
        try:
            iso = datetime.fromisoformat(raw.replace('Z', '+00:00'))
            return iso.date()
        except Exception:
            return None

    @staticmethod
    def _detectar_modulos(ticket: dict) -> list[str]:
        haystack_parts = [
            str(ticket.get('subject') or ''),
            str(ticket.get('description') or ''),
            str(ticket.get('category') or ''),
            str(ticket.get('type') or ''),
            str(ticket.get('service') or ''),
        ]
        cfs = ticket.get('customFieldValues') or ticket.get('customFields') or ticket.get('customfields') or []
        if isinstance(cfs, dict):
            haystack_parts.extend(str(v) for v in cfs.values())
        elif isinstance(cfs, list):
            for cf in cfs:
                if isinstance(cf, dict):
                    haystack_parts.append(str(cf.get('value') or cf.get('customFieldItemValue') or ''))
                    items = cf.get('items') or cf.get('options') or []
                    if isinstance(items, list):
                        for it in items:
                            if isinstance(it, dict):
                                haystack_parts.append(str(it.get('label') or it.get('description') or it.get('value') or ''))
                            else:
                                haystack_parts.append(str(it))
        haystack = ' '.join(haystack_parts).lower()
        encontrados = []
        for spec in MODULOS_PADRAO:
            palavras = spec.get('chaves', ())
            if any(str(p).lower() in haystack for p in palavras):
                encontrados.append(spec['nome'])
        if not encontrados:
            encontrados = list(DETECTAR_FALLBACK)
        return encontrados

    @staticmethod
    def _sugerir_template(modulos_sugeridos: list[str]) -> str:
        if not modulos_sugeridos:
            return 'padrao'
        conjunto = {m.lower() for m in modulos_sugeridos}
        robusto_markers = {'contabilidade', 'financeiro_robusto', 'agricola', 'transportes'}
        medio_markers = {'financeiro_robusto'}
        if conjunto & robusto_markers:
            return 'robusto'
        if conjunto & medio_markers:
            return 'medio'
        return 'padrao'

