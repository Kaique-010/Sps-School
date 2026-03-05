import requests
from datetime import datetime
from django.utils.timezone import now

url = "https://api.movidesk.com/public/v1"
token = "b8ad37b5-67e9-485c-acab-ca7a657090f2"


def parse_movidesk_date(date_str):
    if not date_str:
        return None
    try:
        if "." in date_str:
            parts = date_str.split(".")
            if len(parts[1]) > 6:
                 date_str = f"{parts[0]}.{parts[1][:6]}"
        return datetime.fromisoformat(date_str)
    except Exception:
        return None

def format_delta(delta):
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days} dias, {hours} horas e {minutes} minutos"

def get_tickets_atrasados():
    response = requests.get(
        f"{url}/tickets",
        params={
            "token": token,
            "$select": "id,subject,createdDate,slaSolutionDate,status,owner,ownerTeam,category,lastActionDate,clients,createdBy",
            "$expand": "owner,clients,createdBy",
            "$filter": "status ne 'Resolvido' and status ne 'Fechado' and status ne 'Cancelado'",
            "$orderby": "id",
        },
        headers={
            "Accept": "application/json",
        },
    )
    
    data = response.json()
    formatted_data = []
    
    for ticket in data:
        last_action_date_str = ticket.get("lastActionDate")
        time_since_last_action = "N/A"
        
        last_action_date = parse_movidesk_date(last_action_date_str)
        current_time = datetime.now()

        if last_action_date:
             delta = current_time - last_action_date
             time_since_last_action = format_delta(delta)

        # Cálculo de dias vencidos
        sla_solution_date_str = ticket.get("slaSolutionDate")
        sla_solution_date = parse_movidesk_date(sla_solution_date_str)
        dias_vencido = "Não vencido"
        is_vencido = False
        vencimento_seconds = 0

        if sla_solution_date:
            delta_vencimento = current_time - sla_solution_date
            vencimento_seconds = delta_vencimento.total_seconds()
            # Se delta for positivo, está vencido.
            # Se delta for negativo, ainda não venceu.
            # O usuário pediu "dias vencido a contar da data atual", então mostramos o tempo passado.
            if vencimento_seconds > 0:
                 dias_vencido = format_delta(delta_vencimento)
                 is_vencido = True
            else:
                 dias_vencido = f"Vence em {format_delta(abs(delta_vencimento))}"

        # Tratamento de Cliente
        client_name = "Sem cliente"
        clients = ticket.get("clients")
        if clients and isinstance(clients, list) and len(clients) > 0:
             # Pega o primeiro cliente da lista
             client_data = clients[0]
             # Tenta pegar businessName, se não tiver, tenta name (embora API diga businessName)
             client_name = client_data.get("businessName") or client_data.get("id") or "Cliente sem nome"

        # Tratamento de Dono do Ticket (Owner)
        owner_name = "Sem dono"
        owner = ticket.get("owner")
        if owner:
            owner_name = owner.get("businessName") or owner.get("id") or "Dono sem nome"

        # Tratamento de Com Quem Está (Pode ser Owner ou OwnerTeam)
        # Se tiver owner, está com o owner. Se não, pode estar numa fila de equipe.
        com_quem_esta = ticket.get("ownerTeam") or "Sem equipe"
        if owner_name != "Sem dono":
             com_quem_esta = f"{owner_name} ({com_quem_esta})"
        
        # Tratamento de Assunto (Short Subject)
        subject = ticket.get("subject", "")
        assunto_curto = subject
        if subject and " - " in subject:
            parts = subject.split(" - ")
            if len(parts) >= 2:
                # Pega a segunda parte (índice 1)
                assunto_curto = parts[1].strip()
            # Se quiser pegar até o final (exceto a primeira parte):
            # assunto_curto = " - ".join(parts[1:]).strip()
            # Mas o usuário pediu "intervalo do primeiro - até o outro -", sugerindo a parte do meio.
            # Vou manter a segunda parte como padrão seguro para títulos como "Tipo - Título - Descrição"
        
        formatted_ticket = {
            "id": ticket.get("id"),
            "assunto": subject,
            "assunto_curto": assunto_curto,
            "data_criacao": ticket.get("createdDate"),
            "data_vencimento": ticket.get("slaSolutionDate"),
            "dias_vencido": dias_vencido,
            "is_vencido": is_vencido,
            "vencimento_seconds": vencimento_seconds,
            "status": ticket.get("status"),
            "dono_ticket": owner_name,
            "com_quem_esta": com_quem_esta, 
            "categoria": ticket.get("category"),
            "ultima_acao": ticket.get("lastActionDate"),
            "cliente": client_name,
            "tempo_na_ultima_acao": time_since_last_action
        }
        formatted_data.append(formatted_ticket)

    return formatted_data
