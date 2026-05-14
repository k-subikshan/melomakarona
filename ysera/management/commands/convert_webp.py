
from django.core.management.base import BaseCommand
from ysera.models import ProductImage

from PIL import Image
from django.core.files.base import ContentFile

from io import BytesIO
import os


class Command(BaseCommand):

    help = "Convert existing images to WebP"

    def handle(self, *args, **kwargs):

        for obj in ProductImage.objects.all():

            if not obj.image:
                continue

            old_path = obj.image.path

            # skip already webp
            if old_path.endswith(".webp"):
                continue

            try:

                img = Image.open(old_path)

                if img.mode in ("RGBA", "P"):

                    img = img.convert("RGB")

                webp_name = (
                    os.path.splitext(
                        obj.image.name
                    )[0]
                    + ".webp"
                )

                buffer = BytesIO()

                img.save(
                    buffer,
                    format="WEBP",
                    quality=80,
                    optimize=True
                )

                obj.image.save(
                    webp_name,
                    ContentFile(buffer.getvalue()),
                    save=False
                )

                buffer.close()

                obj.save()

                # delete old image
                if os.path.exists(old_path):

                    os.remove(old_path)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Converted: {webp_name}"
                    )
                )

            except Exception as e:

                self.stdout.write(
                    self.style.ERROR(
                        f"Error: {e}"
                    )
                )