import json
import os

from api.models import Ingredient
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        json_dir = os.path.join(settings.BASE_DIR, 'data')
        json_file = os.path.join(json_dir, 'ingredients.json')
        with open(json_file) as f:
            data = json.loads(f.read())
        imported = []
        for ingredient in data:
            try:
                Ingredient.objects.create(
                    name=ingredient["name"],
                    measurement_unit=ingredient["measurement_unit"],
                )
            except IntegrityError:
                imported.append(ingredient["name"])
