from django.core.management.base import BaseCommand
from faker import Faker
from bearings.models import Bearing

class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        
        bearing_types = [
            "Шарикоподшипник радиальный",
            "Роликоподшипник конический", 
            "Подшипник упорный",
            "Подшипник игольчатый"
        ]

        
        
        for i in range(200):
            in_d=fake.random_int(5, 100)
            bearing_type = fake.random_element(bearing_types)
            Bearing.objects.create(
                name=f"{bearing_type} {fake.random_int(100, 6000)}",
                inner_d=in_d,
                outer_d=in_d + fake.random_int(5, 200),
                height=fake.random_int(5, 50),
                price=fake.random_int(100, 5000),
                ammount=fake.random_int(0, 1000)
            )
        
        self.stdout.write(
            self.style.SUCCESS('Успешно создано 200 подшипников')
        )