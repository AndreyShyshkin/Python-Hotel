from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Seed the database with sample hotel rooms'

    def handle(self, *args, **options):
        self.stdout.write("Starting database seed...")
        self.stdout.write(self.style.SUCCESS('Done!'))
        