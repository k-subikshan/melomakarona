import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "melomakarona.settings")
django.setup()

from ysera.models import ProductImage

for img in ProductImage.objects.all():

    if img.image:

        filename = os.path.basename(img.image.name)

        filename = os.path.splitext(filename)[0] + ".webp"

        new_path = f"images/images/{filename}"

        img.image = new_path

        img.save(update_fields=["image"])

        print("Updated:", new_path)
