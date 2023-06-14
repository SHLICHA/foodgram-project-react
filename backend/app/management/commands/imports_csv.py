import csv

from django.core.management import BaseCommand
from app.models import Ingredient


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('csv_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for csv_file in options['csv_file']:
            data_reader = csv.reader(open(csv_file), delimiter=',')
            for row in data_reader:
                Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
