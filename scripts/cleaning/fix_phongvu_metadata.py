import pandas as pd
from pathlib import Path


BASE = Path("data")
CLEAN_DIR = BASE / "cleaned/phongvu"

CATEGORIES = [
    "laptop",
    "keyboard",
    "monitor",
]

CRAWL_DATE = "2026-09-21"


for category in CATEGORIES:

    file = CLEAN_DIR / f"{category}_products_common.csv"

    df = pd.read_csv(file)

    # Phong Vũ raw API không cung cấp URL trong dữ liệu đã crawl.
    # Giữ URL là NULL, không tự sinh URL giả.
    df["url"] = pd.NA

    # Ngày thực hiện đợt crawl Phong Vũ
    df["crawl_date"] = CRAWL_DATE

    df.to_csv(
        file,
        index=False,
        encoding="utf-8"
    )

    print(
        f"{category.upper()}: "
        f"rows={len(df)}, "
        f"URL missing={df['url'].isna().sum()}, "
        f"crawl_date missing={df['crawl_date'].isna().sum()}"
    )


print()
print("=" * 70)
print("PHONG VU METADATA STANDARDIZATION COMPLETED")
print("=" * 70)
print("URL: giữ NULL vì raw API không cung cấp URL")
print("crawl_date:", CRAWL_DATE)