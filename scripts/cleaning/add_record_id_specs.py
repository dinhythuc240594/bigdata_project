from pathlib import Path
import pandas as pd

BASE = Path("data/cleaned/merged")

CATEGORIES = [
    "laptop",
    "keyboard",
    "monitor",
]


for category in CATEGORIES:

    common_path = BASE / f"{category}_products_common.csv"
    specs_path = BASE / f"{category}_specs.csv"

    common = pd.read_csv(common_path)
    specs = pd.read_csv(specs_path)

    # --------------------------------------------------------
    # KIỂM TRA COMMON ĐÃ CÓ RECORD_ID
    # --------------------------------------------------------

    if "record_id" not in common.columns:
        raise ValueError(
            f"{category}: common chưa có record_id. "
            f"Hãy chạy add_record_id.py trước."
        )

    # --------------------------------------------------------
    # XÁC ĐỊNH SỐ DÒNG TGDĐ
    # --------------------------------------------------------

    tgdd_specs_path = (
        Path("data/cleaned/tgdd") /
        f"{category}_specs.csv"
    )

    tgdd_specs = pd.read_csv(tgdd_specs_path)

    tgdd_count = len(tgdd_specs)

    # Kiểm tra số lượng
    if tgdd_count > len(specs):
        raise ValueError(
            f"{category}: số dòng TGDĐ specs lớn hơn merged specs."
        )

    phongvu_count = len(specs) - tgdd_count

    # --------------------------------------------------------
    # TẠO SOURCE CHO SPECS
    # --------------------------------------------------------

    specs["source"] = (
        ["thegioididong"] * tgdd_count
        +
        ["phongvu"] * phongvu_count
    )

    # --------------------------------------------------------
    # TẠO LOOKUP RECORD_ID
    # --------------------------------------------------------

    lookup = {}

    for _, row in common.iterrows():

        source = str(row["source"]).strip()

        product_id = str(row["product_id"]).strip()

        sku = (
            ""
            if pd.isna(row["sku"])
            else str(row["sku"]).strip()
        )

        # Phong Vũ -> SKU
        if sku:
            key = f"{source}|sku|{sku}"

        # TGDĐ -> product_id
        else:
            key = f"{source}|pid|{product_id}"

        if key in lookup:
            raise ValueError(
                f"{category}: khóa lookup bị trùng: {key}"
            )

        lookup[key] = row["record_id"]

    # --------------------------------------------------------
    # GÁN RECORD_ID CHO SPECS
    # --------------------------------------------------------

    def find_record_id(row):

        source = str(row["source"]).strip()

        product_id = str(row["product_id"]).strip()

        sku = (
            ""
            if pd.isna(row["sku"])
            else str(row["sku"]).strip()
        )

        if sku:
            key = f"{source}|sku|{sku}"
        else:
            key = f"{source}|pid|{product_id}"

        return lookup.get(key)

    specs["record_id"] = specs.apply(
        find_record_id,
        axis=1
    )

    # --------------------------------------------------------
    # KIỂM TRA RECORD_ID MISSING
    # --------------------------------------------------------

    missing = specs["record_id"].isna().sum()

    if missing > 0:

        print("\nCác dòng không tìm được record_id:")

        print(
            specs[
                specs["record_id"].isna()
            ][
                [
                    "product_id",
                    "sku",
                    "source"
                ]
            ].head(20).to_string(index=False)
        )

        raise ValueError(
            f"{category}: {missing} specs "
            f"không tìm được record_id."
        )

    # --------------------------------------------------------
    # XÓA SOURCE TẠM
    # --------------------------------------------------------

    specs.drop(
        columns=["source"],
        inplace=True
    )

    # --------------------------------------------------------
    # ĐƯA RECORD_ID LÊN ĐẦU
    # --------------------------------------------------------

    columns = ["record_id"] + [
        col
        for col in specs.columns
        if col != "record_id"
    ]

    specs = specs[columns]

    # --------------------------------------------------------
    # KIỂM TRA UNIQUE
    # --------------------------------------------------------

    duplicate_count = (
        specs["record_id"]
        .duplicated()
        .sum()
    )

    if duplicate_count > 0:
        raise ValueError(
            f"{category}: có {duplicate_count} "
            f"record_id bị trùng trong specs."
        )

    # --------------------------------------------------------
    # LƯU
    # --------------------------------------------------------

    specs.to_csv(
        specs_path,
        index=False,
        encoding="utf-8-sig"
    )

    print(
        f"{category.upper()}: "
        f"{len(specs)} specs | "
        f"unique record_id = "
        f"{specs['record_id'].nunique()} | "
        f"missing = {missing} | "
        f"duplicates = {duplicate_count}"
    )


print("\n" + "=" * 70)
print("RECORD_ID FOR SPECS COMPLETED")
print("=" * 70)
