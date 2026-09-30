from django.core.management.base import BaseCommand
from registro.servicios import respaldar


class Command(BaseCommand):
    help = "Crea un respaldo de la base de datos (úsalo también en una tarea programada)."

    def handle(self, *args, **opts):
        self.stdout.write(f"Respaldo creado: {respaldar()}")
