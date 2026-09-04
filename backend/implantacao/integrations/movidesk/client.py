import requests
from django.conf import settings


class MovideskError(Exception):
    pass


class MovideskClient:
    def __init__(self):
        self.base_url = settings.MOVIDESK_BASE_URL.rstrip('/')
        self.token = getattr(settings, 'MOVIDESK_TOKEN', '') or getattr(settings, 'MOVIDESK_API_TOKEN', '')
        self.timeout = getattr(settings, 'MOVIDESK_TIMEOUT', 30)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        if self.token:
            self.session.headers['Authorization'] = f'Bearer {self.token}'

    def _build_params(self, extra=None):
        params = {}
        if self.token:
            params['token'] = self.token
        if extra:
            params.update(extra)
        return params

    def obter_ticket(self, ticket_id: int):
        if not self.base_url or not self.token:
            raise MovideskError('MOVIDESK_BASE_URL e MOVIDESK_TOKEN devem estar configurados.')

        candidates = [
            ('GET', f'{self.base_url}/tickets', {'id': ticket_id, '$expand': 'customFields,owner,createdBy,clients'}),
            ('GET', f'{self.base_url}/tickets/{ticket_id}', {'$expand': 'customFields,owner,createdBy,clients'}),
            ('GET', f'{self.base_url}/tickets', {'id': ticket_id}),
        ]

        last_error = None
        for method, url, extra_params in candidates:
            try:
                response = self.session.request(
                    method,
                    url,
                    params=self._build_params(extra_params),
                    timeout=self.timeout,
                )
                if 200 <= response.status_code < 300:
                    data = response.json()
                    if isinstance(data, list):
                        if len(data) == 0:
                            last_error = MovideskError(
                                f'Ticket #{ticket_id} não encontrado no Movidesk. '
                                f'Verifique se o ID existe e se o token tem permissão de leitura.'
                            )
                            continue
                        return data[0]
                    if isinstance(data, dict):
                        if data.get('id') or data.get('ticketId') or data.get('number'):
                            return data
                        items = data.get('items') or data.get('value') or []
                        if isinstance(items, list) and items:
                            return items[0]
                        return data
                    last_error = MovideskError(
                        f'Ticket #{ticket_id}: resposta inesperada do Movidesk. HTTP {response.status_code}.'
                    )
                elif response.status_code in (400, 401, 403, 404, 500):
                    detail = self._extract_error(response)
                    last_error = MovideskError(
                        f'Erro ao consultar ticket {ticket_id}: HTTP {response.status_code}. {detail}'
                    )
                else:
                    detail = self._extract_error(response)
                    last_error = MovideskError(
                        f'Erro ao consultar ticket {ticket_id}: HTTP {response.status_code}. {detail}'
                    )
            except requests.RequestException as exc:
                msg = f'Erro de rede ao consultar ticket {ticket_id}: {exc}'
                last_error = MovideskError(msg)
                last_error.__cause__ = exc

        raise last_error or MovideskError(
            f'Não foi possível consultar o ticket {ticket_id} na API do Movidesk.'
        )

    def _extract_error(self, response):
        try:
            data = response.json()
            if isinstance(data, dict):
                for key in ('message', 'error_description', 'error', 'detail', 'Message'):
                    if data.get(key):
                        return str(data[key])
            if isinstance(data, str):
                return data[:300]
        except Exception:
            pass
        text = (response.text or '').strip()
        if not text:
            return 'Sem detalhes adicionais na resposta.'
        return f'Detalhes: {text[:300]}'
