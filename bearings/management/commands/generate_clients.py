from django.core.management.base import BaseCommand
from faker import Faker
from bearings.models import Client

class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        for _ in range(200):
            Client.objects.create(
                name=fake.name(),
                phone=fake.phone_number()
            )
        self.stdout.write(
            self.style.SUCCESS('Успешно создано 200 клиентов')
        )