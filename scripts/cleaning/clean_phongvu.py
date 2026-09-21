import json
import re
from pathlib import Path

import pandas as pd


# ============================================================
# CONFIG
# ============================================================

RAW_FILE = Path("data/raw/phongvu/products_full.json")
OUTPUT_DIR = Path("data/cleaned/phongvu")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TARGET_CATEGORIES = {
    "laptop": "Laptop - Máy tính xách tay",
    "keyboard": "Bàn phím",
    "monitor": "Màn hình",
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clean_text(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def to_number(value):
    """
    Chuyển:
        22990000
        "22990000"
        "22.990.000"
        "22,990,000"
    thành số.
    """

    if value is None:
        return None

    if isinstance(value, (int, float)):
        if pd.isna(value):
            return None
        return float(value)

    text = str(value).strip()

    if not text:
        return None

    text = re.sub(r"[^\d,.\-]", "", text)

    if not text:
        return None

    if re.fullmatch(r"-?\d{1,3}([.,]\d{3})+", text):
        text = text.replace(".", "").replace(",", "")
    else:
        text = text.replace(",", "")

    try:
        return float(text)
    except ValueError:
        return None


def clean_percent(value):
    value = to_number(value)

    if value is None:
        return None

    return abs(value)


def clean_category(item):
    category_names = {
        clean_text(cat.get("name"))
        for cat in (item.get("categories") or [])
        if isinstance(cat, dict)
    }

    if TARGET_CATEGORIES["laptop"] in category_names:
        return "laptop"

    if TARGET_CATEGORIES["keyboard"] in category_names:
        return "keyboard"

    if TARGET_CATEGORIES["monitor"] in category_names:
        return "monitor"

    return None


def extract_first_number(text, pattern):
    match = re.search(pattern, text, flags=re.IGNORECASE)

    if not match:
        return None

    try:
        return float(match.group(1).replace(",", "."))
    except ValueError:
        return None


# ============================================================
# LAPTOP SPECS
# ============================================================

def extract_laptop_specs(name):
    text = clean_text(name) or ""

    # RAM
    ram_gb = None

    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*(?:GB|GB RAM)\b",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        try:
            ram_gb = float(match.group(1).replace(",", "."))
        except ValueError:
            pass

    # Storage
    storage_gb = None

    # Ưu tiên TB
    match_tb = re.search(
        r"(\d+(?:[.,]\d+)?)\s*TB\b",
        text,
        flags=re.IGNORECASE,
    )

    if match_tb:
        try:
            storage_gb = (
                float(match_tb.group(1).replace(",", ".")) * 1024
            )
        except ValueError:
            pass

    # Nếu không có TB thì tìm GB
    if storage_gb is None:
        gb_matches = re.findall(
            r"(\d+(?:[.,]\d+)?)\s*GB\b",
            text,
            flags=re.IGNORECASE,
        )

        for value in gb_matches:
            try:
                number = float(value.replace(",", "."))

                # Không lấy RAM làm storage
                if ram_gb is None or number != ram_gb:
                    storage_gb = number
                    break

            except ValueError:
                continue

    # Screen size
    screen_size = extract_first_number(
        text,
        r'(\d+(?:[.,]\d+)?)\s*(?:"|inch|in\b)',
    )

    # Weight
    weight_kg = extract_first_number(
        text,
        r'(\d+(?:[.,]\d+)?)\s*kg\b',
    )

    # CPU
    cpu = None

    cpu_patterns = [
        r"(Intel\s+Core\s+Ultra\s+[3579][^(),/]*?)",
        r"(Intel\s+Core\s+i[3579][^(),/]*?)",
        r"(AMD\s+Ryzen\s+[3579][^(),/]*?)",
        r"(Apple\s+M[1-5][^(),/]*)",
        r"(Snapdragon\s+X[^(),/]*)",
    ]

    for pattern in cpu_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            cpu = match.group(1).strip()
            break

    # GPU
    gpu = None

    gpu_patterns = [
        r"(RTX\s*\d{3,4}(?:\s*Ti|\s*SUPER)?)",
        r"(GTX\s*\d{3,4}(?:\s*Ti)?)",
        r"(Radeon\s+RX\s*\d{3,4}[A-Za-z0-9\s]*)",
        r"(Intel\s+Arc\s+[A-Za-z0-9\s]+)",
        r"(Intel\s+UHD\s+Graphics)",
        r"(Intel\s+Iris\s+Xe)",
    ]

    for pattern in gpu_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            gpu = match.group(1).strip()
            break

    return {
        "cpu": cpu,
        "ram_gb": ram_gb,
        "storage_gb": storage_gb,
        "gpu": gpu,
        "screen_size_inch": screen_size,
        "weight_kg": weight_kg,
    }


# ============================================================
# KEYBOARD SPECS
# ============================================================

def extract_keyboard_specs(name):
    text = clean_text(name) or ""
    lower = text.lower()

    # Connection
    connection_type = None

    if "bluetooth" in lower:
        connection_type = "Bluetooth"

    if "wireless" in lower or "không dây" in lower:
        if connection_type:
            connection_type += ", Wireless"
        else:
            connection_type = "Wireless"

    if (
        "có dây" in lower
        or "wired" in lower
        or "usb" in lower
        or "type-c" in lower
        or "type c" in lower
    ):
        if connection_type:
            connection_type += ", Wired"
        else:
            connection_type = "Wired"

    # Keyboard type
    keyboard_type = None

    # Kiểm tra "giả cơ" trước "cơ"
    if "giả cơ" in lower:
        keyboard_type = "Membrane/Hybrid"
    elif "cơ" in lower:
        keyboard_type = "Mechanical"

    # Switch
    switch_type = None

    switch_patterns = [
        r"([A-Za-z0-9\-]+\s+Switch)",
        r"(Switch\s+[A-Za-z0-9\-]+)",
    ]

    for pattern in switch_patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            switch_type = match.group(1).strip()
            break

    # Layout
    layout = None

    layout_patterns = [
        r"\b(60%)\b",
        r"\b(65%)\b",
        r"\b(68%)\b",
        r"\b(75%)\b",
        r"\b(80%)\b",
        r"\b(84%)\b",
        r"\b(87%)\b",
        r"\b(96%)\b",
        r"\b(98%)\b",
        r"\b(TKL)\b",
        r"\b(Full[- ]size)\b",
    ]

    for pattern in layout_patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            layout = match.group(1)
            break

    # Backlight
    backlight = None

    if "rgb" in lower:
        backlight = "RGB"
    elif "led" in lower or "backlit" in lower:
        backlight = "LED"

    return {
        "connection_type": connection_type,
        "keyboard_type": keyboard_type,
        "switch_type": switch_type,
        "layout": layout,
        "backlight": backlight,
    }


# ============================================================
# MONITOR SPECS
# ============================================================

def extract_monitor_specs(name):
    text = clean_text(name) or ""

    # Screen size
    screen_size = extract_first_number(
        text,
        r'(\d+(?:[.,]\d+)?)\s*(?:"|inch|in\b)',
    )

    # Resolution
    resolution = None

    resolution_patterns = [
        r"(\d{3,5}\s*x\s*\d{3,5})",
        r"(4K UHD)",
        r"(Full HD)",
        r"(2K)",
        r"(QHD)",
        r"(WQHD)",
        r"(UHD)",
    ]

    for pattern in resolution_patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            resolution = match.group(1).strip()
            break

    # Refresh rate
    refresh_rate = None

    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*Hz",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        try:
            refresh_rate = float(
                match.group(1).replace(",", ".")
            )
        except ValueError:
            pass

    # Panel type
    panel_type = None

    for panel in [
        "Nano IPS",
        "IPS",
        "VA",
        "TN",
        "OLED",
        "QLED",
        "PLS",
        "AHVA",
    ]:
        if re.search(
            rf"\b{re.escape(panel)}\b",
            text,
            flags=re.IGNORECASE,
        ):
            panel_type = panel
            break

    # Response time
    response_time = None

    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*ms\b",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        try:
            response_time = float(
                match.group(1).replace(",", ".")
            )
        except ValueError:
            pass

    return {
        "screen_size_inch": screen_size,
        "resolution": resolution,
        "refresh_rate_hz": refresh_rate,
        "panel_type": panel_type,
        "response_time_ms": response_time,
    }


# ============================================================
# LOAD RAW DATA
# ============================================================

print("=" * 70)
print("CLEAN PHONG VU")
print("=" * 70)

with open(RAW_FILE, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print("Raw records:", len(raw_data))


# ============================================================
# FILTER + COMMON DATA
# ============================================================

records_by_category = {
    "laptop": [],
    "keyboard": [],
    "monitor": [],
}

seen_sku = {
    "laptop": set(),
    "keyboard": set(),
    "monitor": set(),
}

duplicate_sku_count = {
    "laptop": 0,
    "keyboard": 0,
    "monitor": 0,
}

invalid_price_count = {
    "laptop": 0,
    "keyboard": 0,
    "monitor": 0,
}


for item in raw_data:

    category = clean_category(item)

    if category is None:
        continue

    sku = clean_text(item.get("sku"))

    if sku is None:
        continue

    # SKU mới là khóa duy nhất
    if sku in seen_sku[category]:
        duplicate_sku_count[category] += 1
        continue

    seen_sku[category].add(sku)

    price = to_number(item.get("price"))
    old_price = to_number(
        item.get("supplier_retail_price")
    )

    # Giá phải > 0
    if price is None or price <= 0:
        invalid_price_count[category] += 1
        continue

    discount_amount = to_number(
        item.get("discount_amount")
    )

    discount_percent = clean_percent(
        item.get("discount_percent")
    )

    # Tính discount amount nếu thiếu
    if (
        discount_amount is None
        and old_price is not None
        and old_price >= price
    ):
        discount_amount = old_price - price

    # Tính discount percent nếu thiếu
    if (
        discount_percent is None
        and old_price is not None
        and old_price > 0
        and old_price >= price
    ):
        discount_percent = round(
            (old_price - price) / old_price * 100,
            2,
        )

    product_id = item.get("product_id")

    common = {
        "product_id": product_id,
        "sku": sku,
        "name": clean_text(item.get("name")),
        "brand": clean_text(item.get("brand")),
        "category": category,
        "price_vnd": price,
        "old_price_vnd": old_price,
        "discount_amount_vnd": discount_amount,
        "discount_percent": discount_percent,
        "rating": None,
        "review_count": None,
        "url": clean_text(item.get("url")),
        "source": "phongvu",
        "crawl_date": None,
    }

    records_by_category[category].append(
        {
            "common": common,
            "raw": item,
        }
    )


# ============================================================
# COLUMNS
# ============================================================

common_columns = [
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


# QUAN TRỌNG:
# Specs cũng phải có SKU.
# SKU là khóa liên kết giữa common và specs.

spec_columns = {
    "laptop": [
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
        "product_id",
        "sku",
        "connection_type",
        "keyboard_type",
        "switch_type",
        "layout",
        "backlight",
    ],
    "monitor": [
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
# CREATE OUTPUT FILES
# ============================================================

for category in [
    "laptop",
    "keyboard",
    "monitor",
]:

    entries = records_by_category[category]

    common_rows = []
    spec_rows = []

    for entry in entries:

        common = entry["common"]

        name = common["name"]
        product_id = common["product_id"]
        sku = common["sku"]

        # ------------------------------
        # COMMON
        # ------------------------------

        common_rows.append(common)

        # ------------------------------
        # CATEGORY SPECS
        # ------------------------------

        if category == "laptop":
            specs = extract_laptop_specs(name)

        elif category == "keyboard":
            specs = extract_keyboard_specs(name)

        else:
            specs = extract_monitor_specs(name)

        # Giữ product_id + SKU
        specs = {
            "product_id": product_id,
            "sku": sku,
            **specs,
        }

        spec_rows.append(specs)

    common_df = pd.DataFrame(
        common_rows,
        columns=common_columns,
    )

    specs_df = pd.DataFrame(
        spec_rows,
        columns=spec_columns[category],
    )

    # ========================================================
    # FINAL DEDUPLICATION
    # ========================================================
    #
    # CHỈ deduplicate theo SKU.
    #
    # KHÔNG được:
    # drop_duplicates(subset=["product_id"])
    #
    # Vì một product_id có thể có nhiều SKU.
    # ========================================================

    common_df = common_df.drop_duplicates(
        subset=["sku"],
        keep="first",
    )

    specs_df = specs_df.drop_duplicates(
        subset=["sku"],
        keep="first",
    )

    # ========================================================
    # SORT BY SKU
    # ========================================================

    common_df = common_df.sort_values(
        by="sku",
        kind="stable",
    ).reset_index(drop=True)

    specs_df = specs_df.sort_values(
        by="sku",
        kind="stable",
    ).reset_index(drop=True)

    # ========================================================
    # VALIDATION
    # ========================================================

    common_skus = set(
        common_df["sku"].dropna().astype(str)
    )

    specs_skus = set(
        specs_df["sku"].dropna().astype(str)
    )

    missing_in_specs = common_skus - specs_skus
    missing_in_common = specs_skus - common_skus

    if missing_in_specs:
        raise ValueError(
            f"{category}: SKU có trong common nhưng thiếu trong specs: "
            f"{list(missing_in_specs)[:10]}"
        )

    if missing_in_common:
        raise ValueError(
            f"{category}: SKU có trong specs nhưng thiếu trong common: "
            f"{list(missing_in_common)[:10]}"
        )

    if len(common_df) != len(specs_df):
        raise ValueError(
            f"{category}: Common ({len(common_df)}) "
            f"!= Specs ({len(specs_df)})"
        )

    # ========================================================
    # SAVE
    # ========================================================

    common_path = (
        OUTPUT_DIR /
        f"{category}_products_common.csv"
    )

    specs_path = (
        OUTPUT_DIR /
        f"{category}_specs.csv"
    )

    common_df.to_csv(
        common_path,
        index=False,
        encoding="utf-8-sig",
    )

    specs_df.to_csv(
        specs_path,
        index=False,
        encoding="utf-8-sig",
    )

    # ========================================================
    # REPORT
    # ========================================================

    print("\n" + "-" * 70)
    print(category.upper())
    print("-" * 70)

    print("Records:", len(common_df))

    print(
        "Unique SKU:",
        common_df["sku"].nunique()
    )

    print(
        "Duplicate SKU:",
        common_df["sku"].duplicated().sum()
    )

    print(
        "Unique product_id:",
        common_df["product_id"].nunique()
    )

    print(
        "Duplicate product_id:",
        common_df["product_id"].duplicated().sum()
    )

    print(
        "Missing price:",
        common_df["price_vnd"].isna().sum()
    )

    print(
        "Missing brand:",
        common_df["brand"].isna().sum()
    )

    print(
        "Missing name:",
        common_df["name"].isna().sum()
    )

    print(
        "Missing SKU:",
        common_df["sku"].isna().sum()
    )

    print(
        "Common rows:",
        len(common_df)
    )

    print(
        "Specs rows:",
        len(specs_df)
    )

    print(
        "Invalid price removed:",
        invalid_price_count[category]
    )

    print(
        "Duplicate SKU skipped:",
        duplicate_sku_count[category]
    )

    print("\nOutput:")
    print(common_path)
    print(specs_path)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

total = 0

for category in [
    "laptop",
    "keyboard",
    "monitor",
]:

    common_path = (
        OUTPUT_DIR /
        f"{category}_products_common.csv"
    )

    specs_path = (
        OUTPUT_DIR /
        f"{category}_specs.csv"
    )

    common_df = pd.read_csv(common_path)
    specs_df = pd.read_csv(specs_path)

    print(
        f"{category:10s}: "
        f"{len(common_df):4d} records | "
        f"{common_df['sku'].nunique():4d} unique SKU | "
        f"{common_df['product_id'].nunique():4d} unique product_id | "
        f"common={len(common_df)} specs={len(specs_df)}"
    )

    total += len(common_df)

print("-" * 70)
print("TOTAL CLEANED:", total)
print("Output directory:", OUTPUT_DIR)
print("=" * 70)
