from pathlib import Path
import pandas as pd

BASE = Path("data/cleaned/merged")

CATEGORIES = [
    "laptop",
    "keyboard",
    "monitor",
]


for category in CATEGORIES:

    path = BASE / f"{category}_products_common.csv"

    df = pd.read_csv(path)

    def make_record_id(row):
        source = str(row["source"]).strip()

        sku = row["sku"]

        # Phong Vũ: SKU là unique
        if pd.notna(sku) and str(sku).strip():
            return f"{source}_{str(sku).strip()}"

        # TGDĐ: SKU trống -> dùng product_id
        product_id = str(row["product_id"]).strip()

        return f"{source}_{product_id}"

    df["record_id"] = df.apply(
        make_record_id,
        axis=1
    )

    # Đưa record_id lên đầu
    columns = ["record_id"] + [
        col for col in df.columns
        if col != "record_id"
    ]

    df = df[columns]

    # Kiểm tra record_id
    duplicate_count = df["record_id"].duplicated().sum()

    if duplicate_count > 0:
        raise ValueError(
            f"{category}: phát hiện "
            f"{duplicate_count} record_id bị trùng!"
        )

    df.to_csv(
        path,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\n{category.upper()}")
    print("Records:", len(df))
    print("Unique record_id:", df["record_id"].nunique())
    print("Duplicate record_id:", duplicate_count)

    print("\nSample:")
    print(
        df[
            [
                "record_id",
                "product_id",
                "sku",
                "source",
                "name"
            ]
        ].head(5).to_string(index=False)
    )


print("\n" + "=" * 70)
print("ADD RECORD_ID COMPLETED")
print("=" * 70)
