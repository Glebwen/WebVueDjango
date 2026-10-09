from django.core.management.base import BaseCommand

from faker import Faker

from bearings.models import Client
from bearings.models import Bearing


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        for _ in range(5):
            Client.objects.create(
                name=fake.name(),
                phone=fake.phone_number()
            )
