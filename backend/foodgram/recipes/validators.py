import re
from django.core.exceptions import ValidationError


def validate_name(name):
    if not re.match(r'^[\w\s-]+$', name):
        raise ValidationError('Тэг содержит недопустимые символы.')


def validate_color(color):
    if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color):
        raise ValidationError(
            'Цвет должен быть в формате HEX (#XXXXXX или #XXX).'
        )
