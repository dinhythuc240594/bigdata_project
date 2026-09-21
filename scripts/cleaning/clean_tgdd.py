import json
import re
import csv
from pathlib import Path
from datetime import date


# =========================================================
# PATH
# =========================================================

BASE_DIR = Path.home() / "bigdata_project"

RAW_DIR = BASE_DIR / "data" / "raw" / "tgdd"
OUT_DIR = BASE_DIR / "data" / "cleaned" / "tgdd"

OUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# CẤU HÌNH CATEGORY
# =========================================================

FILES = {
    "laptop": RAW_DIR / "laptop_full.json",
    "keyboard": RAW_DIR / "keyboard_full.json",
    "monitor": RAW_DIR / "monitor_full.json",
}


# =========================================================
# HÀM CHUNG
# =========================================================

def clean_text(value):
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return text


def clean_price(value):
    """
    Chuẩn hóa giá về VND integer.
    """
    if value is None:
        return None

    if isinstance(value, (int, float)):
        if value <= 0:
            return None
        return int(round(value))

    text = str(value).strip()

    if not text:
        return None

    text = text.replace(".", "")
    text = text.replace(",", "")

    match = re.search(r"\d+", text)

    if not match:
        return None

    price = int(match.group())

    return price if price > 0 else None


def clean_discount(value):
    """
    Website lưu discount dạng -10.
    Chuyển thành 10 (% giảm).
    """
    if value is None:
        return None

    try:
        value = float(value)

        if value == 0:
            return 0

        return abs(int(round(value)))

    except (ValueError, TypeError):
        return None


def clean_rating(value):
    if value is None:
        return None

    try:
        rating = float(value)

        if 0 <= rating <= 5:
            return rating

    except (ValueError, TypeError):
        pass

    return None


def clean_integer(value):
    if value is None:
        return None

    try:
        value = int(float(value))

        if value >= 0:
            return value

    except (ValueError, TypeError):
        pass

    return None


# =========================================================
# LAPTOP
# =========================================================

def clean_screen_size(value):
    """
    Ví dụ:
        15.6"
        23.8 inch
        27 inch
    -> float
    """
    if value is None:
        return None

    text = str(value).replace(",", ".")

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:inch|\"|in\b)",
        text,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return None


def clean_ram(value, product_name=None):
    """
    Chuyển:
        16 GB -> 16
        8GB -> 8
        32 GB -> 32
    """
    if value is not None:
        text = str(value).upper().replace(",", ".")

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*GB\b",
            text
        )

        if match:
            return int(float(match.group(1)))

    # fallback từ tên sản phẩm
    if product_name:
        text = str(product_name).upper()

        match = re.search(
            r"\b(\d+(?:\.\d+)?)\s*GB\b",
            text
        )

        if match:
            return int(float(match.group(1)))

    return None


def clean_storage(value, product_name=None):
    """
    Lấy dung lượng hiện tại.

    Ví dụ:
        512 GB SSD NVMe PCIe (Có thể nâng tối đa 2 TB)
        -> 512

        1 TB SSD
        -> 1024
    """

    def convert_to_gb(number, unit):
        number = float(str(number).replace(",", "."))
        unit = unit.upper()

        if unit == "TB":
            return int(number * 1024)

        return int(number)

    if value is not None:

        text = str(value).strip().upper()

        # Chỉ lấy phần dung lượng hiện tại,
        # không lấy phần "TỐI ĐA / NÂNG CẤP TỐI ĐA"
        current_part = re.split(
            r"\bTỐI\s*ĐA\b|\bNÂNG\s*CẤP\s*TỐI\s*ĐA\b",
            text,
            maxsplit=1
        )[0]

        match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(TB|GB)\b",
            current_part
        )

        if match:
            return convert_to_gb(
                match.group(1),
                match.group(2)
            )

    # Fallback từ tên sản phẩm
    if product_name:

        name = str(product_name).upper()

        # Ví dụ:
        # i5, 16GB, 512GB
        match = re.search(
            r"\b\d+(?:[.,]\d+)?\s*GB\s*,\s*"
            r"(\d+(?:[.,]\d+)?)\s*(TB|GB)\b",
            name
        )

        if match:
            return convert_to_gb(
                match.group(1),
                match.group(2)
            )

    return None


def clean_weight(value):
    """
    Chuyển kg về float.
    """
    if value is None:
        return None

    text = str(value).replace(",", ".").strip()

    match = re.search(
        r"(\d+(?:\.\d+)?)",
        text
    )

    if match:
        weight = float(match.group(1))

        if 0 < weight < 20:
            return weight

    return None


# =========================================================
# MONITOR
# =========================================================

def clean_refresh_rate(value):
    """
    Ví dụ:
        144 Hz (OC 175 Hz)
        -> 144

        165Hz
        -> 165
    """
    if value is None:
        return None

    text = str(value).replace(",", ".")

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*Hz",
        text,
        re.IGNORECASE
    )

    if match:
        return int(float(match.group(1)))

    return None


def clean_response_time(value):
    """
    Ví dụ:
        1 ms (MPRT)
        -> 1

        0.3ms
        -> 0.3
    """
    if value is None:
        return None

    text = str(value).replace(",", ".")

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*ms",
        text,
        re.IGNORECASE
    )

    if match:
        return float(match.group(1))

    return None


# =========================================================
# LOAD JSON
# =========================================================

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================================================
# CSV WRITER
# =========================================================

def write_csv(path, rows, fieldnames):

    with open(
        path,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(rows)


# =========================================================
# COMMON SCHEMA
# =========================================================

COMMON_FIELDS = [
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


def build_common(row, category):

    price = clean_price(row.get("price"))
    old_price = clean_price(row.get("old_price"))

    discount_percent = clean_discount(
        row.get("discount")
    )

    discount_amount = None

    if (
        price is not None
        and old_price is not None
        and old_price >= price
    ):
        discount_amount = old_price - price

    product_id = row.get("product_id")

    if product_id is not None:
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            product_id = None

    return {
        "product_id": product_id,
        "sku": clean_text(row.get("product_code")),
        "name": clean_text(row.get("name")),
        "brand": clean_text(row.get("brand")),
        "category": category,
        "price_vnd": price,
        "old_price_vnd": old_price,
        "discount_amount_vnd": discount_amount,
        "discount_percent": discount_percent,
        "rating": clean_rating(row.get("rating")),
        "review_count": clean_integer(
            row.get("review_count")
        ),
        "url": clean_text(row.get("url")),
        "source": clean_text(row.get("source")),
        "crawl_date": clean_text(
            row.get("crawl_date")
        ),
    }


# =========================================================
# LAPTOP SPECS
# =========================================================

LAPTOP_FIELDS = [
    "product_id",
    "cpu",
    "ram_gb",
    "storage_gb",
    "gpu",
    "screen_size_inch",
    "weight_kg",
]


def build_laptop_specs(row):

    return {
        "product_id": row.get("product_id"),
        "cpu": clean_text(row.get("cpu")),
        "ram_gb": clean_ram(
            row.get("ram"),
            row.get("name")
        ),
        "storage_gb": clean_storage(
            row.get("storage"),
            row.get("name")
        ),
        "gpu": clean_text(row.get("gpu")),
        "screen_size_inch": clean_screen_size(
            row.get("screen_size")
        ),
        "weight_kg": clean_weight(
            row.get("weight")
        ),
    }


# =========================================================
# KEYBOARD SPECS
# =========================================================

KEYBOARD_FIELDS = [
    "product_id",
    "connection_type",
    "keyboard_type",
    "switch_type",
    "layout",
    "backlight",
]


def build_keyboard_specs(row):

    return {
        "product_id": row.get("product_id"),
        "connection_type": clean_text(
            row.get("connection_type")
        ),
        "keyboard_type": clean_text(
            row.get("keyboard_type")
        ),
        "switch_type": clean_text(
            row.get("switch_type")
        ),
        "layout": clean_text(
            row.get("layout")
        ),
        "backlight": clean_text(
            row.get("backlight")
        ),
    }


# =========================================================
# MONITOR SPECS
# =========================================================

MONITOR_FIELDS = [
    "product_id",
    "screen_size_inch",
    "resolution",
    "refresh_rate_hz",
    "panel_type",
    "response_time_ms",
]


def build_monitor_specs(row):

    return {
        "product_id": row.get("product_id"),
        "screen_size_inch": clean_screen_size(
            row.get("screen_size")
        ),
        "resolution": clean_text(
            row.get("resolution")
        ),
        "refresh_rate_hz": clean_refresh_rate(
            row.get("refresh_rate")
        ),
        "panel_type": clean_text(
            row.get("panel_type")
        ),
        "response_time_ms": clean_response_time(
            row.get("response_time")
        ),
    }


# =========================================================
# CLEAN TỪNG CATEGORY
# =========================================================

def clean_category(category, input_path):

    print("\n" + "=" * 70)
    print(f"CLEANING: {category.upper()}")
    print("=" * 70)

    raw = load_json(input_path)

    print("Raw records:", len(raw))

    common_rows = []
    spec_rows = []

    seen_ids = set()

    removed_duplicate = 0
    removed_invalid = 0

    for row in raw:

        product_id = row.get("product_id")

        # -------------------------------------------------
        # product_id bắt buộc
        # -------------------------------------------------

        if product_id is None:
            removed_invalid += 1
            continue

        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            removed_invalid += 1
            continue

        # -------------------------------------------------
        # loại duplicate
        # -------------------------------------------------

        if product_id in seen_ids:
            removed_duplicate += 1
            continue

        seen_ids.add(product_id)

        # -------------------------------------------------
        # common
        # -------------------------------------------------

        common = build_common(
            row,
            category
        )

        # Giá là field bắt buộc
        if common["price_vnd"] is None:
            removed_invalid += 1
            continue

        common_rows.append(common)

        # -------------------------------------------------
        # category specs
        # -------------------------------------------------

        if category == "laptop":

            spec_rows.append(
                build_laptop_specs(row)
            )

        elif category == "keyboard":

            spec_rows.append(
                build_keyboard_specs(row)
            )

        elif category == "monitor":

            spec_rows.append(
                build_monitor_specs(row)
            )

    # =====================================================
    # GHI FILE
    # =====================================================

    if category == "laptop":
        spec_fields = LAPTOP_FIELDS
        spec_filename = "laptop_specs.csv"

    elif category == "keyboard":
        spec_fields = KEYBOARD_FIELDS
        spec_filename = "keyboard_specs.csv"

    else:
        spec_fields = MONITOR_FIELDS
        spec_filename = "monitor_specs.csv"

    write_csv(
        OUT_DIR / f"{category}_products_common.csv",
        common_rows,
        COMMON_FIELDS
    )

    write_csv(
        OUT_DIR / spec_filename,
        spec_rows,
        spec_fields
    )

    # =====================================================
    # THỐNG KÊ
    # =====================================================

    print()
    print("Raw records        :", len(raw))
    print("Clean records      :", len(common_rows))
    print("Removed duplicate  :", removed_duplicate)
    print("Removed invalid    :", removed_invalid)

    print()
    print("Output:")
    print(
        " ",
        OUT_DIR / f"{category}_products_common.csv"
    )
    print(
        " ",
        OUT_DIR / spec_filename
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print("=" * 70)
    print("TGDĐ DATA CLEANING")
    print("=" * 70)

    total_raw = 0
    total_clean = 0

    for category, path in FILES.items():

        if not path.exists():
            print(
                f"\nWARNING: Không tìm thấy {path}"
            )
            continue

        clean_category(
            category,
            path
        )


if __name__ == "__main__":
    main()