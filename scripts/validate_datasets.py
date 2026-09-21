import csv
from pathlib import Path


BASE_DIR = Path("/home/hadoop/bigdata_project")

TGDD_FILE = (
    BASE_DIR
    / "data/cleaned/tgdd/laptop_clean.csv"
)

IVIVU_FILE = (
    BASE_DIR
    / "data/cleaned/ivivu/hotel_dalat_clean.csv"
)


def load_csv(path):
    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        return list(csv.DictReader(f))


def check_duplicates(data, key):
    values = [
        row[key]
        for row in data
        if row.get(key)
    ]

    return len(values) - len(set(values))


def missing_count(data, field):
    return sum(
        1
        for row in data
        if row.get(field) in [None, ""]
    )


# ============================================================
# ĐỌC DATASET
# ============================================================

tgdd = load_csv(TGDD_FILE)
ivivu = load_csv(IVIVU_FILE)


# ============================================================
# THÔNG TIN CƠ BẢN
# ============================================================

print("=" * 70)
print("VALIDATION DATASET")
print("=" * 70)

print()
print("1. SO LUONG RECORD")
print("-" * 70)

print(f"TGDĐ  : {len(tgdd)}")
print(f"iVIVU : {len(ivivu)}")
print(f"TONG  : {len(tgdd) + len(ivivu)}")


# ============================================================
# DUPLICATE
# ============================================================

print()
print("2. DUPLICATE")
print("-" * 70)

tgdd_dup = check_duplicates(tgdd, "url")
ivivu_dup = check_duplicates(ivivu, "hotel_id")

print(f"TGDĐ duplicate URL       : {tgdd_dup}")
print(f"iVIVU duplicate hotel_id : {ivivu_dup}")


# ============================================================
# MISSING TGDĐ
# ============================================================

tgdd_fields = [
    "name",
    "brand",
    "price_vnd",
    "old_price_vnd",
    "discount_percent",
    "rating",
    "review_count",
    "screen_size_inch",
    "cpu",
    "gpu",
    "ram_gb",
    "storage_gb",
    "weight_kg",
    "url",
    "source",
    "crawl_date",
]

print()
print("3. MISSING VALUES - TGDĐ")
print("-" * 70)

for field in tgdd_fields:
    print(
        f"{field:20}: "
        f"{missing_count(tgdd, field)}"
    )


# ============================================================
# MISSING IVIVU
# ============================================================

ivivu_fields = [
    "hotel_id",
    "hotel_code",
    "name",
    "star_rating",
    "review_score",
    "review_count",
    "min_price_vnd",
    "max_price_vnd",
    "deal_price_vnd",
    "address",
    "latitude",
    "longitude",
    "description",
    "facilities",
    "location_tags",
    "hotel_url",
    "source",
    "crawl_date",
    "check_in",
    "check_out",
]

print()
print("4. MISSING VALUES - iVIVU")
print("-" * 70)

for field in ivivu_fields:
    print(
        f"{field:20}: "
        f"{missing_count(ivivu, field)}"
    )


# ============================================================
# KIỂM TRA GIÁ TGDĐ
# ============================================================

print()
print("5. KIEM TRA GIA TGDĐ")
print("-" * 70)

invalid_tgdd_price = 0

for row in tgdd:
    value = row.get("price_vnd")

    if value:
        try:
            if float(value) <= 0:
                invalid_tgdd_price += 1
        except ValueError:
            invalid_tgdd_price += 1

print(
    f"price_vnd <= 0 / invalid : "
    f"{invalid_tgdd_price}"
)


# ============================================================
# KIỂM TRA GIÁ IVIVU
# ============================================================

print()
print("6. KIEM TRA GIA iVIVU")
print("-" * 70)

invalid_ivivu_price = 0

for row in ivivu:
    for field in [
        "min_price_vnd",
        "max_price_vnd",
    ]:
        value = row.get(field)

        if value:
            try:
                if float(value) <= 0:
                    invalid_ivivu_price += 1
            except ValueError:
                invalid_ivivu_price += 1

print(
    f"min/max price invalid : "
    f"{invalid_ivivu_price}"
)


# ============================================================
# SOURCE
# ============================================================

print()
print("7. SOURCE")
print("-" * 70)

tgdd_sources = set(
    row["source"]
    for row in tgdd
)

ivivu_sources = set(
    row["source"]
    for row in ivivu
)

print("TGDĐ source :", tgdd_sources)
print("iVIVU source:", ivivu_sources)


# ============================================================
# FINAL
# ============================================================

total = len(tgdd) + len(ivivu)

print()
print("=" * 70)
print("KET LUAN")
print("=" * 70)

if total > 1000:
    print(
        f"PASS: Tong dataset = {total} records > 1000"
    )
else:
    print(
        f"FAIL: Tong dataset = {total} records <= 1000"
    )

print("=" * 70)
