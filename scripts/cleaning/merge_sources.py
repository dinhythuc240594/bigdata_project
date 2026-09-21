from pathlib import Path
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

TGDD_DIR = Path("data/cleaned/tgdd")
PHONGVU_DIR = Path("data/cleaned/phongvu")
OUTPUT_DIR = Path("data/cleaned/merged")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


CATEGORIES = [
    "laptop",
    "keyboard",
    "monitor",
]


COMMON_COLUMNS = [
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
# FUNCTION
# ============================================================

def read_csv(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file:\n{path}"
        )

    return pd.read_csv(path)


def normalize_common(df, source):
    """
    Chuẩn hóa common về cùng schema.
    """

    # Đảm bảo đủ cột
    for col in COMMON_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA

    df = df[COMMON_COLUMNS].copy()

    # Chuẩn hóa source
    df["source"] = source

    return df


def normalize_specs(df, category):
    """
    Chuẩn hóa specs về cùng schema.
    """

    columns = SPEC_COLUMNS[category]

    for col in columns:
        if col not in df.columns:
            df[col] = pd.NA

    return df[columns].copy()


# ============================================================
# START
# ============================================================

print("=" * 75)
print("MERGE TGDĐ + PHONG VŨ")
print("=" * 75)


total_common = 0
total_specs = 0


for category in CATEGORIES:

    print("\n" + "-" * 75)
    print(category.upper())
    print("-" * 75)

    # --------------------------------------------------------
    # COMMON
    # --------------------------------------------------------

    tgdd_common_path = (
        TGDD_DIR /
        f"{category}_products_common.csv"
    )

    phongvu_common_path = (
        PHONGVU_DIR /
        f"{category}_products_common.csv"
    )

    tgdd_common = read_csv(tgdd_common_path)
    phongvu_common = read_csv(phongvu_common_path)

    tgdd_count = len(tgdd_common)
    phongvu_count = len(phongvu_common)

    tgdd_common = normalize_common(
        tgdd_common,
        "thegioididong",
    )

    phongvu_common = normalize_common(
        phongvu_common,
        "phongvu",
    )

    merged_common = pd.concat(
        [
            tgdd_common,
            phongvu_common,
        ],
        ignore_index=True,
    )

    # --------------------------------------------------------
    # SPECS
    # --------------------------------------------------------

    tgdd_specs_path = (
        TGDD_DIR /
        f"{category}_specs.csv"
    )

    phongvu_specs_path = (
        PHONGVU_DIR /
        f"{category}_specs.csv"
    )

    tgdd_specs = read_csv(tgdd_specs_path)
    phongvu_specs = read_csv(phongvu_specs_path)

    tgdd_specs_count = len(tgdd_specs)
    phongvu_specs_count = len(phongvu_specs)

    tgdd_specs = normalize_specs(
        tgdd_specs,
        category,
    )

    phongvu_specs = normalize_specs(
        phongvu_specs,
        category,
    )

    merged_specs = pd.concat(
        [
            tgdd_specs,
            phongvu_specs,
        ],
        ignore_index=True,
    )

    # --------------------------------------------------------
    # VALIDATION COMMON
    # --------------------------------------------------------

    expected_common = (
        tgdd_count +
        phongvu_count
    )

    if len(merged_common) != expected_common:
        raise ValueError(
            f"{category}: số common sau merge không đúng. "
            f"Expected={expected_common}, "
            f"Actual={len(merged_common)}"
        )

    # --------------------------------------------------------
    # VALIDATION SPECS
    # --------------------------------------------------------

    expected_specs = (
        tgdd_specs_count +
        phongvu_specs_count
    )

    if len(merged_specs) != expected_specs:
        raise ValueError(
            f"{category}: số specs sau merge không đúng. "
            f"Expected={expected_specs}, "
            f"Actual={len(merged_specs)}"
        )

    # --------------------------------------------------------
    # VALIDATE SOURCE
    # --------------------------------------------------------

    source_counts = (
        merged_common["source"]
        .value_counts()
        .to_dict()
    )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    common_output = (
        OUTPUT_DIR /
        f"{category}_products_common.csv"
    )

    specs_output = (
        OUTPUT_DIR /
        f"{category}_specs.csv"
    )

    merged_common.to_csv(
        common_output,
        index=False,
        encoding="utf-8-sig",
    )

    merged_specs.to_csv(
        specs_output,
        index=False,
        encoding="utf-8-sig",
    )

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print(f"TGDĐ common     : {tgdd_count}")
    print(f"Phong Vũ common : {phongvu_count}")
    print(f"Merged common   : {len(merged_common)}")

    print()

    print(f"TGDĐ specs      : {tgdd_specs_count}")
    print(f"Phong Vũ specs  : {phongvu_specs_count}")
    print(f"Merged specs    : {len(merged_specs)}")

    print()

    print("Source distribution:")
    for source, count in source_counts.items():
        print(f"  {source:18s}: {count}")

    print()

    print(
        "Duplicate source + product_id:",
        merged_common.duplicated(
            subset=["source", "product_id"]
        ).sum()
    )

    print(
        "Missing price:",
        merged_common["price_vnd"].isna().sum()
    )

    print(
        "Price <= 0:",
        (
            merged_common["price_vnd"] <= 0
        ).sum()
    )

    print("\nOutput:")
    print(common_output)
    print(specs_output)

    total_common += len(merged_common)
    total_specs += len(merged_specs)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("MERGE SUMMARY")
print("=" * 75)

print(
    f"Laptop   : "
    f"{len(pd.read_csv(OUTPUT_DIR / 'laptop_products_common.csv'))}"
)

print(
    f"Keyboard : "
    f"{len(pd.read_csv(OUTPUT_DIR / 'keyboard_products_common.csv'))}"
)

print(
    f"Monitor  : "
    f"{len(pd.read_csv(OUTPUT_DIR / 'monitor_products_common.csv'))}"
)

print("-" * 75)

print("TOTAL COMMON:", total_common)
print("TOTAL SPECS :", total_specs)

print("-" * 75)
print("Output directory:", OUTPUT_DIR)
print("=" * 75)
