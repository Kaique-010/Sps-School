import os
import mimetypes
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

    def _request(self, method, endpoint, *, params=None, json=None):
        if not self.base_url or not self.token:
            raise MovideskError('MOVIDESK_BASE_URL e MOVIDESK_TOKEN devem estar configurados.')

        url = f'{self.base_url}/{endpoint.lstrip("/")}'

        try:
            response = self.session.request(
                method,
                url,
                params=self._build_params(params),
                json=json,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise MovideskError(f'Erro de comunicação com o Movidesk: {exc}') from exc

        if not 200 <= response.status_code < 300:
            detail = self._extract_error(response)
            raise MovideskError(f'Erro na API do Movidesk: HTTP {response.status_code}. {detail}')

        if not response.content:
            return None

        try:
            return response.json()
        except ValueError:
            return response.text

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
                            last_error = MovideskError(f'Ticket #{ticket_id} não encontrado no Movidesk.')
                            continue
                        return data[0]
                    if isinstance(data, dict):
                        if data.get('id') or data.get('ticketId') or data.get('number'):
                            return data
                        items = data.get('items') or data.get('value') or []
                        if isinstance(items, list) and items:
                            return items[0]
                        return data
                else:
                    detail = self._extract_error(response)
                    last_error = MovideskError(f'Erro ao consultar ticket {ticket_id}: HTTP {response.status_code}. {detail}')
            except requests.RequestException as exc:
                last_error = MovideskError(f'Erro de rede ao consultar ticket {ticket_id}: {exc}')

        raise last_error or MovideskError(f'Não foi possível consultar o ticket {ticket_id} na API do Movidesk.')

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

    def atualizar_ticket(self, ticket_id: int, payload: dict):
        return self._request(
            "PATCH",
            "/tickets",
            params={"id": ticket_id},
            json=payload,
        )

    def enviar_anexos(self, ticket_id: int, anexos, action_id: int):
        if not self.base_url or not self.token:
            raise MovideskError('MOVIDESK_BASE_URL e MOVIDESK_TOKEN devem estar configurados.')

        endpoint = "/ticketFileUpload" if "/public/v1" in self.base_url else "/public/v1/ticketFileUpload"
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        params = {
            "token": self.token,
            "id": ticket_id,
            "actionId": action_id,
        }

        # Trata nome e MIME type dinamicamente do objeto InMemoryUploadedFile (Django) ou File
        caminho_original = getattr(anexos, "name", "arquivo.pdf")
        nome_arquivo = os.path.basename(caminho_original)
        
        # Detecta tipo do arquivo ou define padrão octet-stream/pdf
        mime_type, _ = mimetypes.guess_type(nome_arquivo)
        mime_type = getattr(anexos, "content_type", None) or mime_type or "application/octet-stream"

        # Salva o Content-Type atual da sessão
        content_type_original = self.session.headers.pop('Content-Type', None)

        try:
            # Garante o posicionamento do ponteiro do arquivo no início
            if hasattr(anexos, 'seek'):
                anexos.seek(0)

            # Realiza a requisição sem o 'Content-Type: application/json' na sessão
            resposta = self.session.post(
                url,
                params=params,
                files={
                    "anexos": (
                        nome_arquivo,
                        anexos,
                        mime_type,
                    ),
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise MovideskError(f'Erro de rede ao enviar anexos ao ticket {ticket_id}: {exc}') from exc
        finally:
            # Restaura o Content-Type padrão da sessão
            if content_type_original:
                self.session.headers['Content-Type'] = content_type_original

        if not 200 <= resposta.status_code < 300:
            detail = self._extract_error(resposta)
            raise MovideskError(f'Erro ao enviar anexos ao ticket {ticket_id}: HTTP {resposta.status_code}. {detail}')

        if not resposta.content:
            return None

        try:
            return resposta.json()
        except ValueError:
            return resposta.text