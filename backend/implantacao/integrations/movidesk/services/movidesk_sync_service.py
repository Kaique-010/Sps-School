from ..client import MovideskClient
from implantacao.models import OrigemMovidesk


class MovideskSyncService:

    TIPO_ACAO_INTERNA = 1
    TIPO_ACAO_PUBLICA = 2
    ID_IMPLANTADOR = '1289670546'

    def __init__(self, client=None):
        self.client = client or MovideskClient()

    def atualizar_ticket(self, implantacao, payload):
        origem = OrigemMovidesk.objects.filter(
            implantacao=implantacao
        ).first()

        if not origem:
            raise ValueError(
                "Esta implantação não possui ticket vinculado ao Movidesk."
            )

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
        origem = OrigemMovidesk.objects.filter(
            implantacao=implantacao
        ).first()

        if not origem:
            raise ValueError(
                "Esta implantação não possui ticket vinculado ao Movidesk."
            )

        if not descricao or not descricao.strip():
            raise ValueError(
                "A descrição da ação é obrigatória."
            )

        ticket = self.client.obter_ticket(origem.ticket_id)

        actions = []

        for action in ticket.get("actions", []):
            actions.append({
                "id": action["id"],
                "type": action["type"],
                "description": action["description"],
                "createdBy": self.ID_IMPLANTADOR,
            })

        actions.append({
            "id": 0,
            "type": tipo,
            "description": descricao,
            "createdBy": self.ID_IMPLANTADOR,
        
        })

        return self.client.atualizar_ticket(
            ticket_id=origem.ticket_id,
            payload={
                "actions": actions,
            },
        )