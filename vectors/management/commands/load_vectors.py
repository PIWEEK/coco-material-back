import pathlib

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from vectors.models import Vector

class Command(BaseCommand):
    help = 'Loads vectors from a specific directory. Files must have the schema: tag1_tag2.svg or tag1_tag2-1.svg'

    def add_arguments(self, parser):
        parser.add_argument('source_dir')

    def handle(self, *args, **options):
        source_dir = options['source_dir']

        for source_vector in pathlib.Path(source_dir).glob('*.svg'):
            file_name = source_vector.name
            if file_name.find('-') > -1:
                tags_str = file_name[:file_name.find('-')]
            else:
                tags_str = file_name[:file_name.find('.')]

            tags = tags_str.split('_')

            vector = Vector(name=file_name)
            with open(source_vector, 'rb') as f:
                content = File(f)
                vector.svg.save(file_name, content, save=True)

            vector.tags.add(*tags)

        self.stdout.write(self.style.SUCCESS('Successfully loaded vectors!'))
