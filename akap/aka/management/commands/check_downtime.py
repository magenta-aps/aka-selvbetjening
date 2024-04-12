from aka.clients.prisme import Prisme, PrismeNotFoundException
from aka.models import PrismeDown
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set downtime placard based on prisme availability"

    def handle(self, *args, **options):
        try:
            try:
                prisme = Prisme()
                prisme.check_cvr("12950160")  # Magenta Grønland
                # prisme.check_cvr("86631628")  # Fujitsu
            except PrismeNotFoundException:
                # Didn't find company (server returned "not found")
                # We don't care; we got a response, so the connection works
                pass
            PrismeDown.set(False)
        except:  # noqa
            # Some different error
            PrismeDown.set(True)
            raise
