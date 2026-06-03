from django.core.management.base import BaseCommand
from ysera.models import ProductImage

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        for img in ProductImage.objects.all():

            try:
                img.save()
                self.stdout.write(f"Resized: {img.image.name}")

            except Exception as e:
                self.stdout.write(f"Error: {e}")