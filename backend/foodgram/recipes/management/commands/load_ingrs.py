import csv
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.load_ingredients()

    def load_ingredients(self, file='ingredients.csv'):
        file_path = f'./data/{file}'
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                ingredient, created = Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
                if created:
                    self.stdout.write(
                        f"Created new ingredient: {ingredient}"
                        )
                else:
                    self.stdout.write(
                        f"Ingredient already exists: {ingredient}"
                        )
