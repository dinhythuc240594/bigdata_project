import json
import re
import csv
from pathlib import Path


# ============================================================
# 1. ĐƯỜNG DẪN
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data/raw/tgdd/laptop_full.json"
OUTPUT_FILE = BASE_DIR / "data/cleaned/tgdd/laptop_clean.csv"


# ============================================================
# 2. HÀM CHUẨN HÓA CHUỖI
# ============================================================

def clean_text(value):
    """
    Xóa khoảng trắng thừa và chuẩn hóa chuỗi.
    """
    if value is None:
        return None

    value = str(value)

    # Thay nhiều khoảng trắng bằng 1 khoảng trắng
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================================
# 3. CHUYỂN GIÁ TIỀN
# ============================================================
def clean_price(value):
    """
    Chuyển giá về số nguyên VND.

    Giá 0 hoặc âm được xem là dữ liệu không hợp lệ
    và chuyển thành None.
    """

    if value is None or value == "":
        return None

    if isinstance(value, (int, float)):
        value = int(value)

        if value <= 0:
            return None

        return value

    value = str(value)

    value = re.sub(r"[^\d]", "", value)

    if not value:
        return None

    value = int(value)

    if value <= 0:
        return None

    return value


# ============================================================
# 4. CHUYỂN PHẦN TRĂM GIẢM GIÁ
# ============================================================

def clean_discount(value):
    """
    Ví dụ:
        -7% -> -7
        7%  -> 7
    """

    if value is None or value == "":
        return None

    match = re.search(r"-?\d+", str(value))

    if not match:
        return None

    return int(match.group())


# ============================================================
# 5. CHUYỂN RATING
# ============================================================

def clean_rating(value):
    """
    Chuẩn hóa rating thành float.
    """

    if value is None or value == "":
        return None

    try:
        rating = float(value)

        if 0 <= rating <= 5:
            return rating

    except (ValueError, TypeError):
        pass

    return None


# ============================================================
# 6. CHUYỂN SỐ REVIEW
# ============================================================

def clean_integer(value):
    """
    Chuyển dữ liệu số về integer.

    Ví dụ:
        "1.250" -> 1250
        "1250"  -> 1250
    """

    if value is None or value == "":
        return None

    if isinstance(value, (int, float)):
        return int(value)

    value = str(value)

    value = re.sub(r"[^\d]", "", value)

    if not value:
        return None

    return int(value)


# ============================================================
# 7. TÁCH KÍCH THƯỚC MÀN HÌNH
# ============================================================

def clean_screen_size(value):
    """
    Ví dụ:

        15.6" -> 15.6
        14"   -> 14
        16 inch -> 16
    """

    if value is None:
        return None

    match = re.search(r"(\d+(?:[.,]\d+)?)", str(value))

    if not match:
        return None

    try:
        return float(match.group(1).replace(",", "."))

    except ValueError:
        return None


# ============================================================
# 8. TÁCH RAM
# ============================================================

def clean_ram(value):
    """
    Ví dụ:

        16 GB -> 16
        8GB   -> 8
        16 GB DDR5 -> 16
    """

    if value is None:
        return None

    match = re.search(r"(\d+(?:[.,]\d+)?)\s*GB", str(value), re.I)

    if not match:
        return None

    try:
        return float(match.group(1).replace(",", "."))

    except ValueError:
        return None

# ============================================================
# 9. TÁCH DUNG LƯỢNG SSD/HDD
# ============================================================
def clean_storage(value, product_name=None):
    """
    Chuẩn hóa dung lượng lưu trữ hiện tại của laptop về GB.

    Ưu tiên:
    1. Trường storage trong dữ liệu raw.
    2. Nếu storage chỉ chứa thông tin nâng cấp -> lấy từ tên sản phẩm.
    3. Khi lấy từ tên, chỉ nhận mẫu RAM + STORAGE:
       Ví dụ:
       - 16GB, 512GB
       - 32GB, 1TB
       - 16 GB, 512 GB

    Không lấy nhầm VRAM GPU:
       RTX 3050 6GB
       RTX 5060 8GB
       RTX 5070 8GB
    """

    def convert_to_gb(number, unit):
        number = float(str(number).replace(",", "."))
        unit = unit.upper()

        if unit == "TB":
            return int(number * 1024)

        return int(number)

    # ==========================================================
    # 1. ƯU TIÊN TRƯỜNG STORAGE RAW
    # ==========================================================

    if value is not None:
        text = str(value).strip().upper()

        # Bỏ phần mô tả dung lượng nâng cấp tối đa
        # Ví dụ:
        # "512 GB SSD ... tối đa 2 TB"
        # => chỉ xét phần trước "TỐI ĐA"
        current_part = re.split(
            r"\bTỐI\s*ĐA\b|\bNÂNG\s*CẤP\s*TỐI\s*ĐA\b",
            text,
            maxsplit=1
        )[0]

        # Tìm dung lượng hiện tại đầu tiên
        match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(TB|GB)\b",
            current_part
        )

        if match:
            return convert_to_gb(match.group(1), match.group(2))

    # ==========================================================
    # 2. FALLBACK: LẤY TỪ TÊN SẢN PHẨM
    # ==========================================================

    if product_name is not None:
        name = str(product_name).upper()

        # Tìm mẫu:
        # 16GB, 512GB
        # 32GB, 1TB
        # 16 GB, 512 GB
        #
        # Quan trọng:
        # chỉ lấy dung lượng đứng NGAY SAU dung lượng RAM.
        # Vì vậy sẽ không lấy:
        # RTX 3050 6GB
        # RTX 5070 8GB

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

    # Không xác định được
    return None



# ============================================================
# 10. CHUYỂN TRỌNG LƯỢNG
# ============================================================
def clean_weight(value):
    """
    Chuẩn hóa trọng lượng về kg.

    Ví dụ:
        1.79 kg -> 1.79
        1.79    -> 1.79
        2 kg    -> 2.0
    """

    if value is None or value == "":
        return None

    text = str(value).strip()

    # Trường hợp có kg
    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*kg",
        text,
        re.I
    )

    if match:
        try:
            return float(
                match.group(1).replace(",", ".")
            )
        except ValueError:
            return None

    # Trường hợp chỉ có số, ví dụ "1.79"
    match = re.search(
        r"^\s*(\d+(?:[.,]\d+)?)\s*$",
        text
    )

    if match:
        try:
            return float(
                match.group(1).replace(",", ".")
            )
        except ValueError:
            return None

    return None



# ============================================================
# 11. CLEAN MỘT RECORD
# ============================================================
def clean_product(product):

    return {
        "name": clean_text(product.get("name")),

        "brand": clean_text(product.get("brand")),

        "price_vnd": clean_price(
            product.get("price")
        ),

        "old_price_vnd": clean_price(
            product.get("old_price")
        ),

        "discount_percent": clean_discount(
            product.get("discount")
        ),

        "rating": clean_rating(
            product.get("rating")
        ),

        "review_count": clean_integer(
            product.get("review_count")
        ),

        "screen_size_inch": clean_screen_size(
            product.get("screen_size")
        ),

        "cpu": clean_text(
            product.get("cpu")
        ),

        "gpu": clean_text(
            product.get("gpu")
        ),

        "ram_gb": clean_ram(
            product.get("ram")
        ),

        "storage_gb": clean_storage(
            product.get("storage"),
            product.get("name")
        ),

        "weight_kg": clean_weight(
            product.get("weight")
        ),

        "url": clean_text(
            product.get("url")
        ),

        "source": "thegioididong",

        "crawl_date": clean_text(
            product.get("crawl_date")
        )
    }


# ============================================================
# 12. ĐỌC RAW DATA
# ============================================================

print("=" * 60)
print("BẮT ĐẦU DATA CLEANING - THẾ GIỚI DI ĐỘNG")
print("=" * 60)

print(f"Input : {INPUT_FILE}")
print(f"Output: {OUTPUT_FILE}")

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print(f"\nRaw records: {len(raw_data)}")


# ============================================================
# 13. CLEAN DATA
# ============================================================

cleaned_data = []
removed_count = 0

for product in raw_data:

    cleaned_product = clean_product(product)

    # Chỉ giữ record có tên
    if not cleaned_product["name"]:
        removed_count += 1
        continue

    # Chỉ giữ record có URL
    if not cleaned_product["url"]:
        removed_count += 1
        continue

    # Giá là trường bắt buộc đối với dữ liệu laptop
    # Nếu không có giá thì loại record khỏi cleaned dataset
    if cleaned_product["price_vnd"] is None:
        print(
            f"Loại record thiếu giá: "
            f"{cleaned_product['name']}"
        )
        removed_count += 1
        continue

    cleaned_data.append(cleaned_product)


# ============================================================
# 14. LOẠI BỎ URL TRÙNG
# ============================================================

unique_data = []
seen_urls = set()

for product in cleaned_data:

    url = product["url"]

    if url in seen_urls:
        continue

    seen_urls.add(url)

    unique_data.append(product)


cleaned_data = unique_data

# ============================================================
# 15. KẾT QUẢ
# ============================================================
print("\n" + "=" * 60)
print("KẾT QUẢ DATA CLEANING")
print("=" * 60)

print(f"Raw records       : {len(raw_data)}")
print(f"Cleaned records    : {len(cleaned_data)}")
print(f"Removed records    : {removed_count}")
print(f"Unique URLs        : {len(seen_urls)}")
print(f"Missing price      : {sum(1 for x in cleaned_data if x['price_vnd'] is None)}")


# ============================================================
# 16. TẠO THƯ MỤC OUTPUT
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 17. GHI CSV
# ============================================================
fieldnames = [
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
    "crawl_date"
]

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8-sig",
    newline=""
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(cleaned_data)


# ============================================================
# 18. THỐNG KÊ
# ============================================================

print("\n" + "=" * 60)
print("KẾT QUẢ CLEANING")
print("=" * 60)

print(f"Raw records       : {len(raw_data)}")
print(f"Cleaned records   : {len(cleaned_data)}")
print(f"Removed records   : {len(raw_data) - len(cleaned_data)}")
print(f"Unique URLs       : {len(seen_urls)}")

print("\nOutput:")
print(OUTPUT_FILE)

print("=" * 60)
print("HOÀN TẤT")
print("=" * 60)
