from django.core.management import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Load Tags'

    def handle(self, *args, **options):
        self.load_tags()

    def load_tags(self):
        tags = [
            {'name': 'Breakfast', 'color': '#FC4103', 'slug': 'breakfast'},
            {'name': 'Lunch', 'color': '#03FC03', 'slug': 'lunch'},
            {'name': 'Dinner', 'color': '#0352FC', 'slug': 'dinner'}
        ]
        Tag.objects.bulk_create(Tag(**tag) for tag in tags)
        self.stdout.write(self.style.SUCCESS('All tags have been loaded!'))
