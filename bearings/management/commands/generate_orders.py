# bearings/management/commands/generate_orders.py
from django.core.management.base import BaseCommand
from faker import Faker
from bearings.models import Order, OrderComposition, Client, Bearing

class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        
        clients = list(Client.objects.all())
        bearings = list(Bearing.objects.all())
        
        if not clients:
            self.stdout.write(
                self.style.ERROR('Сначала создайте клиентов (generate_clients)')
            )
            return
            
        if not bearings:
            self.stdout.write(
                self.style.ERROR('Сначала создайте подшипники (generate_bearings)')
            )
            return
        
        for i in range(100):
            order = Order.objects.create(
                number=fake.unique.random_int(1000, 9999),
                client=fake.random_element(clients)
            )
            
            num_items = fake.random_int(1, 5)
            for _ in range(num_items):
                bearing = fake.random_element(bearings)
                OrderComposition.objects.create(
                    order=order,
                    bearing=bearing,
                    ammount=fake.random_int(1, 50)
                )
        
        self.stdout.write(
            self.style.SUCCESS('Успешно создано 100 заказов с составами')
        )