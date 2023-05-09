from django.core.management import BaseCommand
from recipes.models import Tag

class Command(BaseCommand):
    help = 'Загрузка Tags'

    def handle(self, *args, **kwargs):
        data = [
            {'name': 'Завтрак', 'color': '#FC4103', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#03FC03', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#0352FC', 'slug': 'dinner'}]
        Tag.objects.bulk_create(Tag(**tag) for tag in data)
        self.stdout.write(self.style.SUCCESS('Все тэги загружены!'))