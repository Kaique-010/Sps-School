from django.core.management.base import BaseCommand
from tkts.services.tkts_atrasados import get_tickets_atrasados
import json

class Command(BaseCommand):
    help = 'Busca tickets atrasados no Movidesk'

    def handle(self, *args, **options):
        self.stdout.write('Buscando tickets atrasados...')
        try:
            data = get_tickets_atrasados()
            self.stdout.write(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Erro ao buscar tickets: {e}'))
