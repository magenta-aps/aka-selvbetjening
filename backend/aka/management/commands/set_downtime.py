from aka.models import PrismeDown
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Set downtime placard (up or down)"

    def add_arguments(self, parser):
        parser.add_argument("state", type=str)

    def handle(self, *args, **options):
        state = options["state"]
        if state == "down":
            PrismeDown.set(True)
        elif state == "up":
            PrismeDown.set(False)
        else:
            print("must specify either 'up' or 'down'")
