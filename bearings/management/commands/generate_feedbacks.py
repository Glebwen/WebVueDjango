# bearings/management/commands/generate_deliveries.py
from django.core.management.base import BaseCommand
from faker import Faker
from bearings.models import Feedback, Client

class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        
        clients = list(Client.objects.all())
        
        if not clients:
            self.stdout.write(
                self.style.ERROR('Сначала создайте клиентов (generate_clients)')
            )
            return
            
    
        for i in range(200):
            Feedback.objects.create(
                review=fake.paragraph(nb_sentences=1),
                client=fake.random_element(clients)
            )
            
            
        
        self.stdout.write(
            self.style.SUCCESS('Успешно создано 200 отзывов')
        )