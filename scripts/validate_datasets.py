#!/usr/bin/env python3

"""
BIG DATA PROJECT
Validate cleaned datasets: Thế Giới Di Động + Phong Vũ

Kiểm tra:
1. File tồn tại và đọc được
2. Số lượng record
3. Duplicate record_id / product_id / sku
4. Missing values
5. Giá sản phẩm không hợp lệ
6. Discount hợp lệ
7. Source hợp lệ
8. Category hợp lệ
9. Tính nhất quán common <-> specs
10. Kiểm tra dữ liệu merged
"""

from pathlib import Path
import csv
import sys
from collections import Counter


# ============================================================
# 1. CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

CLEANED_DIR = BASE_DIR / "data" / "cleaned"

TGDD_DIR = CLEANED_DIR / "tgdd"
MERGED_DIR = CLEANED_DIR / "merged"


VALID_SOURCES = {
    "thegioididong",
    "phongvu",
}

VALID_CATEGORIES = {
    "laptop",
    "keyboard",
    "monitor",
}


DATASETS = {
    "laptop": {
        "common": MERGED_DIR / "laptop_products_common.csv",
        "specs": MERGED_DIR / "laptop_specs.csv",
        "key": "record_id",
    },
    "keyboard": {
        "common": MERGED_DIR / "keyboard_products_common.csv",
        "specs": MERGED_DIR / "keyboard_specs.csv",
        "key": "record_id",
    },
    "monitor": {
        "common": MERGED_DIR / "monitor_products_common.csv",
        "specs": MERGED_DIR / "monitor_specs.csv",
        "key": "record_id",
    },
}


# ============================================================
# 2. EXPECTED COLUMNS
# ============================================================

COMMON_COLUMNS = [
    "record_id",
    "product_id",
    "sku",
    "name",
    "brand",
    "category",
    "price_vnd",
    "old_price_vnd",
    "discount_amount_vnd",
    "discount_percent",
    "rating",
    "review_count",
    "url",
    "source",
    "crawl_date",
]

SPEC_COLUMNS = {
    "laptop": [
        "record_id",
        "product_id",
        "sku",
        "cpu",
        "ram_gb",
        "storage_gb",
        "gpu",
        "screen_size_inch",
        "weight_kg",
    ],

    "keyboard": [
        "record_id",
        "product_id",
        "sku",
        "connection_type",
        "keyboard_type",
        "switch_type",
        "layout",
        "backlight",
    ],

    "monitor": [
        "record_id",
        "product_id",
        "sku",
        "screen_size_inch",
        "resolution",
        "refresh_rate_hz",
        "panel_type",
        "response_time_ms",
    ],
}


# ============================================================
# 3. UTILITIES
# ============================================================

def print_line(char="=", length=75):
    print(char * length)


def load_csv(path):
    """Đọc CSV UTF-8 và trả về list[dict]."""

    if not path.exists():
        print(f"[ERROR] Không tìm thấy file: {path}")
        return []

    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                print(f"[ERROR] File không có header: {path}")
                return []

            rows = list(reader)

        print(f"[OK] {path.relative_to(BASE_DIR)} -> {len(rows):,} records")
        return rows

    except Exception as e:
        print(f"[ERROR] Không thể đọc {path}: {e}")
        return []


def missing_count(rows, field):
    return sum(
        1
        for row in rows
        if str(row.get(field, "")).strip() == ""
    )


def duplicate_count(rows, field):
    values = [
        str(row.get(field, "")).strip()
        for row in rows
        if str(row.get(field, "")).strip()
    ]

    counter = Counter(values)

    return sum(
        count - 1
        for count in counter.values()
        if count > 1
    )


def duplicate_values(rows, field):
    values = [
        str(row.get(field, "")).strip()
        for row in rows
        if str(row.get(field, "")).strip()
    ]

    counter = Counter(values)

    return {
        value: count
        for value, count in counter.items()
        if count > 1
    }


def to_float(value):
    try:
        value = str(value).strip()

        if value == "":
            return None

        return float(value)

    except (ValueError, TypeError):
        return None


def to_int(value):
    try:
        value = str(value).strip()

        if value == "":
            return None

        return int(float(value))

    except (ValueError, TypeError):
        return None


def check_columns(rows, expected, file_name):
    if not rows:
        return False

    actual = set(rows[0].keys())
    expected_set = set(expected)

    missing = expected_set - actual
    extra = actual - expected_set

    ok = True

    if missing:
        print(f"[ERROR] {file_name}: thiếu cột:")
        for col in sorted(missing):
            print(f"        - {col}")
        ok = False

    if extra:
        print(f"[INFO] {file_name}: cột dư:")
        for col in sorted(extra):
            print(f"        + {col}")

    if ok:
        print(f"[OK] Schema {file_name}: đầy đủ cột")

    return ok


# ============================================================
# 4. LOAD DATA
# ============================================================

print_line()
print("VALIDATE DATASETS - BIG DATA PROJECT")
print("Nguồn: Thế Giới Di Động + Phong Vũ")
print_line()

print(f"Project root: {BASE_DIR}")
print(f"Cleaned data: {CLEANED_DIR}")
print()

datasets = {}

for category, config in DATASETS.items():

    print_line("-")
    print(f"LOAD DATA: {category.upper()}")

    common = load_csv(config["common"])
    specs = load_csv(config["specs"])

    datasets[category] = {
        "common": common,
        "specs": specs,
    }

print()


# ============================================================
# 5. SCHEMA VALIDATION
# ============================================================

print_line()
print("1. KIỂM TRA SCHEMA")
print_line()

for category, data in datasets.items():

    print(f"\n[{category.upper()}]")

    check_columns(
        data["common"],
        COMMON_COLUMNS,
        f"{category}_products_common.csv"
    )

    check_columns(
        data["specs"],
        SPEC_COLUMNS[category],
        f"{category}_specs.csv"
    )


# ============================================================
# 6. RECORD COUNT
# ============================================================

print_line()
print("2. THỐNG KÊ SỐ LƯỢNG RECORD")
print_line()

total_products = 0

for category, data in datasets.items():

    common_count = len(data["common"])
    specs_count = len(data["specs"])

    print(
        f"{category.capitalize():10s} | "
        f"common = {common_count:>5,} | "
        f"specs = {specs_count:>5,}"
    )

    if common_count != specs_count:
        print(
            f"  [WARNING] Common và Specs không bằng nhau!"
        )

    total_products += common_count

print("-" * 75)
print(f"TỔNG PRODUCTS: {total_products:,}")

if total_products >= 1000:
    print("[OK] Đạt yêu cầu > 1000 records.")
else:
    print("[WARNING] Chưa đạt 1000 records.")


# ============================================================
# 7. DUPLICATE CHECK
# ============================================================

print_line()
print("3. KIỂM TRA DUPLICATE")
print_line()

for category, data in datasets.items():

    print(f"\n[{category.upper()}]")

    common = data["common"]
    specs = data["specs"]

    for field in ["record_id", "product_id", "sku"]:

        common_dup = duplicate_count(common, field)
        specs_dup = duplicate_count(specs, field)

        print(
            f"{field:12s} | "
            f"common duplicate = {common_dup:>5,} | "
            f"specs duplicate = {specs_dup:>5,}"
        )


# ============================================================
# 8. MISSING VALUES - COMMON
# ============================================================

print_line()
print("4. MISSING VALUES - COMMON")
print_line()

for category, data in datasets.items():

    rows = data["common"]

    print(f"\n[{category.upper()}]")

    for field in COMMON_COLUMNS:

        count = missing_count(rows, field)

        print(
            f"{field:22s}: {count:>5,}"
        )


# ============================================================
# 9. MISSING VALUES - SPECS
# ============================================================

print_line()
print("5. MISSING VALUES - SPECS")
print_line()

for category, data in datasets.items():

    rows = data["specs"]

    print(f"\n[{category.upper()}]")

    for field in SPEC_COLUMNS[category]:

        count = missing_count(rows, field)

        print(
            f"{field:22s}: {count:>5,}"
        )


# ============================================================
# 10. PRICE VALIDATION
# ============================================================

print_line()
print("6. KIỂM TRA GIÁ")
print_line()

for category, data in datasets.items():

    rows = data["common"]

    invalid_price = 0
    invalid_old_price = 0
    invalid_discount_amount = 0
    invalid_discount_percent = 0

    for row in rows:

        price = to_float(row.get("price_vnd"))
        old_price = to_float(row.get("old_price_vnd"))
        discount_amount = to_float(
            row.get("discount_amount_vnd")
        )
        discount_percent = to_float(
            row.get("discount_percent")
        )

        # price phải > 0 nếu có giá
        if price is not None and price <= 0:
            invalid_price += 1

        # old_price phải > 0 nếu có
        if old_price is not None and old_price <= 0:
            invalid_old_price += 1

        # discount amount không được âm
        if discount_amount is not None and discount_amount < 0:
            invalid_discount_amount += 1

        # discount percent phải nằm trong 0-100
        if (
            discount_percent is not None
            and (
                discount_percent < 0
                or discount_percent > 100
            )
        ):
            invalid_discount_percent += 1

    print(f"\n[{category.upper()}]")

    print(
        f"price <= 0                  : {invalid_price}"
    )

    print(
        f"old_price <= 0              : {invalid_old_price}"
    )

    print(
        f"discount_amount < 0         : {invalid_discount_amount}"
    )

    print(
        f"discount_percent ngoài 0-100: {invalid_discount_percent}"
    )


# ============================================================
# 11. DISCOUNT CONSISTENCY
# ============================================================

print_line()
print("7. KIỂM TRA TÍNH NHẤT QUÁN DISCOUNT")
print_line()

for category, data in datasets.items():

    rows = data["common"]

    invalid = 0
    checked = 0

    for row in rows:

        price = to_float(row.get("price_vnd"))
        old_price = to_float(row.get("old_price_vnd"))
        discount_amount = to_float(
            row.get("discount_amount_vnd")
        )

        if (
            price is not None
            and old_price is not None
            and discount_amount is not None
        ):

            checked += 1

            expected = old_price - price

            # sai lệch cho phép 1 VND
            if abs(expected - discount_amount) > 1:
                invalid += 1

    print(
        f"{category.capitalize():10s} | "
        f"checked = {checked:>5,} | "
        f"invalid = {invalid:>5,}"
    )


# ============================================================
# 12. RATING VALIDATION
# ============================================================

print_line()
print("8. KIỂM TRA RATING")
print_line()

for category, data in datasets.items():

    rows = data["common"]

    invalid_rating = 0
    invalid_review_count = 0

    for row in rows:

        rating = to_float(row.get("rating"))
        review_count = to_int(row.get("review_count"))

        if rating is not None:
            if rating < 0 or rating > 5:
                invalid_rating += 1

        if review_count is not None:
            if review_count < 0:
                invalid_review_count += 1

    print(f"\n[{category.upper()}]")

    print(
        f"rating ngoài 0-5 : {invalid_rating}"
    )

    print(
        f"review_count < 0  : {invalid_review_count}"
    )


# ============================================================
# 13. SOURCE VALIDATION
# ============================================================

print_line()
print("9. KIỂM TRA SOURCE")
print_line()

for category, data in datasets.items():

    rows = data["common"]

    source_counter = Counter(
        str(row.get("source", "")).strip()
        for row in rows
    )

    print(f"\n[{category.upper()}]")

    for source, count in source_counter.items():

        print(
            f"{source or '[EMPTY]':25s}: {count:>5,}"
        )

        if source not in VALID_SOURCES:
            print(
                f"  [WARNING] Source không nằm trong danh sách "
                f"nguồn dự kiến."
            )


# ============================================================
# 14. CATEGORY VALIDATION
# ============================================================

print_line()
print("10. KIỂM TRA CATEGORY")
print_line()

for category, data in datasets.items():

    rows = data["common"]

    invalid_category = 0

    for row in rows:

        row_category = str(
            row.get("category", "")
        ).strip().lower()

        if row_category not in VALID_CATEGORIES:
            invalid_category += 1

    print(
        f"{category.capitalize():10s} | "
        f"invalid category = {invalid_category}"
    )


# ============================================================
# 15. COMMON <-> SPECS INTEGRITY
# ============================================================

print_line()
print("11. KIỂM TRA COMMON <-> SPECS")
print_line()

for category, data in datasets.items():

    common_ids = {
        str(row.get("record_id", "")).strip()
        for row in data["common"]
        if str(row.get("record_id", "")).strip()
    }

    specs_ids = {
        str(row.get("record_id", "")).strip()
        for row in data["specs"]
        if str(row.get("record_id", "")).strip()
    }

    common_missing_specs = common_ids - specs_ids
    specs_missing_common = specs_ids - common_ids

    print(f"\n[{category.upper()}]")

    print(
        f"Common không có Specs : "
        f"{len(common_missing_specs):>5,}"
    )

    print(
        f"Specs không có Common : "
        f"{len(specs_missing_common):>5,}"
    )

    if not common_missing_specs and not specs_missing_common:
        print("[OK] Quan hệ Common <-> Specs đầy đủ.")


# ============================================================
# 16. RECORD_ID EMPTY CHECK
# ============================================================

print_line()
print("12. KIỂM TRA RECORD_ID")
print_line()

for category, data in datasets.items():

    for table_name in ["common", "specs"]:

        rows = data[table_name]

        empty = missing_count(rows, "record_id")
        duplicates = duplicate_count(rows, "record_id")

        print(
            f"{category:10s} | "
            f"{table_name:6s} | "
            f"empty = {empty:>4} | "
            f"duplicate = {duplicates:>4}"
        )


# ============================================================
# 17. PRICE STATISTICS
# ============================================================

print_line()
print("13. THỐNG KÊ GIÁ SẢN PHẨM")
print_line()

for category, data in datasets.items():

    prices = []

    for row in data["common"]:

        price = to_float(row.get("price_vnd"))

        if price is not None and price > 0:
            prices.append(price)

    if not prices:
        print(f"{category}: không có dữ liệu giá.")
        continue

    prices_sorted = sorted(prices)

    n = len(prices_sorted)

    if n % 2 == 1:
        median = prices_sorted[n // 2]
    else:
        median = (
            prices_sorted[n // 2 - 1]
            + prices_sorted[n // 2]
        ) / 2

    average = sum(prices) / len(prices)

    print(f"\n[{category.upper()}]")

    print(
        f"Số sản phẩm có giá : {len(prices):,}"
    )

    print(
        f"Giá thấp nhất      : {min(prices):,.0f} VND"
    )

    print(
        f"Giá cao nhất       : {max(prices):,.0f} VND"
    )

    print(
        f"Giá trung bình     : {average:,.0f} VND"
    )

    print(
        f"Giá trung vị       : {median:,.0f} VND"
    )


# ============================================================
# 18. SOURCE DISTRIBUTION
# ============================================================

print_line()
print("14. PHÂN BỐ DỮ LIỆU THEO NGUỒN")
print_line()

for category, data in datasets.items():

    counter = Counter(
        str(row.get("source", "")).strip()
        for row in data["common"]
    )

    print(f"\n[{category.upper()}]")

    for source, count in counter.items():

        print(
            f"{source:25s}: {count:>5,}"
        )


# ============================================================
# 19. SUMMARY
# ============================================================

print()
print_line()
print("TỔNG KẾT")
print_line()

print(
    f"Tổng số sản phẩm sau cleaning/merge: "
    f"{total_products:,}"
)

print()

for category, data in datasets.items():

    common_count = len(data["common"])
    specs_count = len(data["specs"])

    common_ids = {
        str(row.get("record_id", "")).strip()
        for row in data["common"]
        if str(row.get("record_id", "")).strip()
    }

    specs_ids = {
        str(row.get("record_id", "")).strip()
        for row in data["specs"]
        if str(row.get("record_id", "")).strip()
    }

    common_dup = duplicate_count(
        data["common"],
        "record_id"
    )

    specs_dup = duplicate_count(
        data["specs"],
        "record_id"
    )

    missing_relation = (
        len(common_ids - specs_ids)
        + len(specs_ids - common_ids)
    )

    status = "PASS"

    if common_count != specs_count:
        status = "CHECK"

    if common_dup > 0 or specs_dup > 0:
        status = "CHECK"

    if missing_relation > 0:
        status = "CHECK"

    print(
        f"{category.capitalize():10s} | "
        f"Common={common_count:>5,} | "
        f"Specs={specs_count:>5,} | "
        f"Status={status}"
    )

print()

if total_products >= 1000:
    print("[PASS] Dataset đạt yêu cầu số lượng > 1000 records.")
else:
    print("[WARNING] Dataset chưa đạt 1000 records.")

print()
print("Validation hoàn tất.")
print_line()
