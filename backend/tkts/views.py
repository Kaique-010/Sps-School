from django.shortcuts import render
from django.views.generic import TemplateView
from tkts.services.tkts_atrasados import get_tickets_atrasados
from datetime import timedelta

class PainelAtrasadosView(TemplateView):
    template_name = "tkts/painel_atrasados.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter todos os tickets
        tickets = get_tickets_atrasados()
        
        # Filtros
        owner_filter = self.request.GET.get('owner')
        status_filter = self.request.GET.get('status')
        client_filter = self.request.GET.get('client')
        
        # Aplicar filtros
        filtered_tickets = tickets
        if owner_filter:
            filtered_tickets = [t for t in filtered_tickets if t.get('dono_ticket') == owner_filter]
        if status_filter:
            filtered_tickets = [t for t in filtered_tickets if t.get('status') == status_filter]
        if client_filter:
            filtered_tickets = [t for t in filtered_tickets if t.get('cliente') == client_filter]
            
        # KPIs e Métricas (sobre os dados filtrados)
        total_tickets = len(filtered_tickets)
        vencidos = [t for t in filtered_tickets if t.get('is_vencido')]
        no_prazo = [t for t in filtered_tickets if not t.get('is_vencido')]
        
        total_vencidos = len(vencidos)
        total_no_prazo = len(no_prazo)
        
        # Média de atraso (apenas dos vencidos)
        media_atraso_str = "0h"
        if total_vencidos > 0:
            total_seconds_atraso = sum(t.get('vencimento_seconds', 0) for t in vencidos)
            avg_seconds = total_seconds_atraso / total_vencidos
            avg_delta = timedelta(seconds=avg_seconds)
            days = avg_delta.days
            hours, remainder = divmod(avg_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            media_atraso_str = f"{days}d {hours}h {minutes}m"

        # Listas para Filtros (Dropdows) - baseadas no total original para dar opções
        all_owners = sorted(list(set(t.get('dono_ticket') for t in tickets if t.get('dono_ticket'))))
        all_statuses = sorted(list(set(t.get('status') for t in tickets if t.get('status'))))
        all_clients = sorted(list(set(t.get('cliente') for t in tickets if t.get('cliente'))))

        # Agrupamentos para Gráficos/Tabelas Resumo
        tickets_by_owner = {}
        for t in filtered_tickets:
            owner = t.get('dono_ticket', 'Sem dono')
            tickets_by_owner[owner] = tickets_by_owner.get(owner, 0) + 1
            
        tickets_by_status = {}
        for t in filtered_tickets:
            status = t.get('status', 'Sem status')
            tickets_by_status[status] = tickets_by_status.get(status, 0) + 1
            
        tickets_by_client = {}
        for t in filtered_tickets:
            client = t.get('cliente', 'Sem cliente')
            tickets_by_client[client] = tickets_by_client.get(client, 0) + 1

        context.update({
            'tickets': filtered_tickets,
            'total_tickets': total_tickets,
            'total_vencidos': total_vencidos,
            'total_no_prazo': total_no_prazo,
            'media_atraso': media_atraso_str,
            'all_owners': all_owners,
            'all_statuses': all_statuses,
            'all_clients': all_clients,
            'tickets_by_owner': dict(sorted(tickets_by_owner.items(), key=lambda item: item[1], reverse=True)),
            'tickets_by_status': dict(sorted(tickets_by_status.items(), key=lambda item: item[1], reverse=True)),
            'tickets_by_client': dict(sorted(tickets_by_client.items(), key=lambda item: item[1], reverse=True)),
            'selected_owner': owner_filter,
            'selected_status': status_filter,
            'selected_client': client_filter,
        })
        
        return context
