from ..client import MovideskClient
from implantacao.models import OrigemMovidesk


class MovideskSyncService:

    TIPO_ACAO_INTERNA = 1
    TIPO_ACAO_PUBLICA = 2
    ID_IMPLANTADOR = '1289670546'

    def __init__(self, client=None):
        self.client = client or MovideskClient()

    def atualizar_ticket(self, implantacao, payload):
        origem = OrigemMovidesk.objects.filter(implantacao=implantacao).first()

        if not origem:
            raise ValueError("Esta implantação não possui ticket vinculado ao Movidesk.")

        return self.client.atualizar_ticket(
            ticket_id=origem.ticket_id,
            payload=payload,
        )

    def adicionar_acao_interna(self, implantacao, descricao):
        return self._adicionar_acao(
            implantacao=implantacao,
            descricao=descricao,
            tipo=self.TIPO_ACAO_INTERNA,
        )

    def adicionar_acao_publica(self, implantacao, descricao):
        return self._adicionar_acao(
            implantacao=implantacao,
            descricao=descricao,
            tipo=self.TIPO_ACAO_PUBLICA,
        )

    def _adicionar_acao(self, implantacao, descricao, tipo):
        origem = OrigemMovidesk.objects.filter(implantacao=implantacao).first()

        if not origem:
            raise ValueError("Esta implantação não possui ticket vinculado ao Movidesk.")

        if not descricao or not descricao.strip():
            raise ValueError("A descrição da ação é obrigatória.")

        # Envia apenas a ação nova, sem re-enviar histórico antigo
        payload = {
            "actions": [
                {
                    "id": 0,
                    "type": tipo,
                    "description": descricao,
                    "createdBy": {
                        "id": self.ID_IMPLANTADOR,
                    },
                }
            ]
        }

        return self.client.atualizar_ticket(
            ticket_id=origem.ticket_id,
            payload=payload,
        )

    def adicionar_acao_com_anexo(self, implantacao, descricao, arquivos, tipo=None):
        tipo = tipo or self.TIPO_ACAO_INTERNA

        # 1. Cria a ação no ticket
        resposta = self._adicionar_acao(implantacao, descricao, tipo)

        origem = OrigemMovidesk.objects.get(implantacao=implantacao)

        # 2. Tenta extrair as ações da resposta
        acoes = []
        if isinstance(resposta, dict):
            acoes = resposta.get("actions", [])

        # Se a API não retornou o ticket atualizado na resposta, busca o ticket atualizado
        if not acoes:
            ticket_atualizado = self.client.obter_ticket(origem.ticket_id)
            if isinstance(ticket_atualizado, dict):
                acoes = ticket_atualizado.get("actions", [])

        if not acoes:
            raise ValueError("Não foi possível obter o ID da ação criada no Movidesk para anexar os arquivos.")

        # A ação recém-criada é sempre a última da lista
        action_id = acoes[-1]["id"]

        # 3. Faz o envio de cada anexo vinculado a essa ação
        resultados = []
        for arq in arquivos:
            res = self.client.enviar_anexos(
                ticket_id=origem.ticket_id,
                action_id=action_id,
                anexos=arq,
            )
            resultados.append(res)

        return resultados