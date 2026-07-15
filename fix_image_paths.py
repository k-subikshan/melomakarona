"""
Run with:
    python manage.py shell < fix_image_paths.py

Updates ProductImage.image paths from:
    images/images/.../file.webp
to:
    images/file.webp
"""

from ysera.models import ProductImage

count = 0

for img in ProductImage.objects.all():
    if not img.image:
        continue

    old_path = img.image.name
    filename = old_path.split("/")[-1]
    new_path = f"images/{filename}"

    if old_path != new_path:
        print(f"{old_path} -> {new_path}")
        img.image.name = new_path
        img.save(update_fields=["image"])
        count += 1

print(f"\nDone! Updated {count} image paths.")
