from ysera.models import ProductImage

updated = 0

for img in ProductImage.objects.all():
    if img.image:
        old = img.image.name
        new = old

        # Keep replacing until only one "images/" remains
        while "images/images/" in new:
            new = new.replace("images/images/", "images/")

        if old != new:
            img.image.name = new
            img.save(update_fields=["image"])
            updated += 1
            print(f"{old} -> {new}")

print(f"\nUpdated {updated} records.")