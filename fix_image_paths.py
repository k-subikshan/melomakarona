import difflib
import glob
import os

from django.conf import settings

from ysera.models import ProductImage


def build_prefix_map():
    prefix_map = {}
    for path in glob.glob(str(settings.MEDIA_ROOT / "images" / "*.webp")):
        basename = os.path.basename(path)
        prefix = basename.split("_")[0].split(".")[0]
        prefix_map.setdefault(prefix, []).append(basename)
    return prefix_map


def find_best_file(db_name, candidates):
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    normalized = db_name.replace("images/images/", "images/")
    normalized_base = os.path.basename(normalized)
    if normalized_base in candidates:
        return normalized_base

    return max(
        candidates,
        key=lambda candidate: difflib.SequenceMatcher(
            None, normalized_base, candidate
        ).ratio(),
    )


def normalize_image_path(db_name, prefix_map):
    normalized = db_name.replace("images/images/", "images/")
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, normalized)):
        return normalized

    prefix = os.path.basename(normalized).split("_")[0].split(".")[0]
    best = find_best_file(normalized, prefix_map.get(prefix, []))
    if best:
        return f"images/{best}"
    return normalized


def main():
    prefix_map = build_prefix_map()
    updated = 0
    still_missing = 0

    for img in ProductImage.objects.exclude(image="").exclude(image__isnull=True):
        if not img.image:
            continue

        old = img.image.name
        new = normalize_image_path(old, prefix_map)

        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, new)):
            still_missing += 1
            print(f"MISSING: {old} -> {new}")
            continue

        if old != new:
            ProductImage.objects.filter(pk=img.pk).update(image=new)
            updated += 1
            print(f"{old} -> {new}")

    print(f"\nUpdated {updated} records.")
    if still_missing:
        print(f"Still missing on disk: {still_missing}")


if __name__ == "__main__":
    main()
