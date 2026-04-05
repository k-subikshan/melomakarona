import pandas as pd
import re
from ysera.models import Product, Category
from django.utils.text import slugify
import uuid

def clean_price(value):
    value = str(value)
    match = re.search(r'\d+', value)
    return float(match.group()) if match else 0.0


def run():
    df = pd.read_excel('Jewels price list.xlsx')

    df.columns = df.columns.str.strip()
    df = df.fillna("")
    
    added = 0
    skipped = 0
    addeder=9999

    for _, row in df.iterrows():
        addeder += 1
        try:
            name = str(row['JEWEL NAME']).strip()
            price_text = str(row['PRICE']).strip().lower()

            # 🚫 Skip rent products
            if price_text.startswith("rent"):
                print(f"⏭ Skipped (Rent): {name}")
                skipped += 1
                continue

            # 🚫 Skip duplicates
            if Product.objects.filter(p_name=name).exists():
                print(f"⚠️ Already exists: {name}")
                skipped += 1
                continue

            category, _ = Category.objects.get_or_create(
                c_name=row['COLLECTION']
            )

            price = clean_price(row['PRICE'])

            slug = slugify(name) + "-" + str(uuid.uuid4())[:8]

            Product.objects.create(
                p_name=name,
                point1=row['TYPES'],
                point2=row['OCCASIONS'],
                brand_name="Jewels",
                desc=name,
                size=row['SIZE'],
                price=price,
                del_price=0,
                rentalprice=0,
                availablity='0',
                save_upto=1,
                category=category,
                delivery_times=1,
                new='yes',
                stock_status='in stock',
                where_in_home='bestseller',
                where_to_display='none',
                slug=slug
            )

            print(f"✅ Added: {name}")
            added += 1

        except Exception as e:
            print(f"❌ Error in row: {row}")
            print(e)

    print("\n🎉 Import Completed!")
    print(f"✅ Added: {added}")
    print(f"⏭ Skipped: {skipped}")