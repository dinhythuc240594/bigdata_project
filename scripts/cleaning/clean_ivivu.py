import csv
import json
import re
from pathlib import Path


# ============================================================
# 1. ĐƯỜNG DẪN
# ============================================================

INPUT_FILE = Path(
    "/home/hadoop/bigdata_project/"
    "data/raw/ivivu/hotel_dalat_full.json"
)

OUTPUT_FILE = Path(
    "/home/hadoop/bigdata_project/"
    "data/cleaned/ivivu/hotel_dalat_clean.csv"
)


# ============================================================
# 2. HÀM LÀM SẠCH GIÁ
# ============================================================

def clean_price(value):
    """
    Chuyển giá dạng:

        '2.881.440 VND'
        '880.000 VND'

    thành:

        2881440
        880000

    Giá rỗng -> None
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    # Chỉ giữ chữ số
    digits = re.sub(r"[^\d]", "", text)

    if not digits:
        return None

    return int(digits)


def clean_deal_price(value):
    """
    deal_price = 0 được xem là không có deal,
    nên chuyển thành NULL.
    """

    if value is None:
        return None

    try:
        value = float(value)
    except (ValueError, TypeError):
        return None

    if value <= 0:
        return None

    return int(value)


# ============================================================
# 3. HÀM LÀM SẠCH TEXT
# ============================================================

def clean_text(value):
    """
    Xóa khoảng trắng thừa.
    """

    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return re.sub(r"\s+", " ", text)


# ============================================================
# 4. HÀM LÀM SẠCH LIST TEXT
# ============================================================

def clean_list_text(value):
    """
    Ví dụ:

    ['Hồ bơi nước ấm', 'Phong cách Châu Âu']

    thành:

    'Hồ bơi nước ấm; Phong cách Châu Âu'
    """

    if not value:
        return None

    if isinstance(value, list):
        values = []

        for item in value:
            text = clean_text(item)

            if text:
                values.append(text)

        if values:
            return "; ".join(values)

        return None

    return clean_text(value)


# ============================================================
# 5. LÀM SẠCH FACILITIES
# ============================================================

def clean_facilities(value):
    """
    facilities có dạng:

    [
        {'id': 0, 'name': 'Hồ bơi nước ấm'},
        {'id': 1, 'name': 'Phòng gia đình'}
    ]

    Chỉ lấy name.
    """

    if not value:
        return None

    if not isinstance(value, list):
        return clean_text(value)

    names = []

    for item in value:
        if isinstance(item, dict):
            name = clean_text(item.get("name"))

            if name:
                names.append(name)

    if names:
        return "; ".join(names)

    return None


# ============================================================
# 6. LÀM SẠCH LOCATION TAGS
# ============================================================

def clean_location_tags(value):
    """
    Ví dụ:

    [
        {'id': 74057, 'name': 'Trung tâm TP Đà Lạt'}
    ]

    thành:

    'Trung tâm TP Đà Lạt'
    """

    if not value:
        return None

    if not isinstance(value, list):
        return clean_text(value)

    names = []

    for item in value:
        if isinstance(item, dict):
            name = clean_text(item.get("name"))

            if name:
                names.append(name)

    if names:
        return "; ".join(names)

    return None


# ============================================================
# 7. LÀM SẠCH URL
# ============================================================

def clean_url(value):
    """
    Chuyển URL tương đối:

        /khach-san-da-lat/abc

    thành:

        https://www.ivivu.com/khach-san-da-lat/abc
    """

    if value is None:
        return None

    url = str(value).strip()

    if not url:
        return None

    if url.startswith("http://") or url.startswith("https://"):
        return url

    if url.startswith("/"):
        return "https://www.ivivu.com" + url

    return "https://www.ivivu.com/" + url


# ============================================================
# 8. ĐỌC RAW DATA
# ============================================================

print("=" * 60)
print("BAT DAU CLEANING IVIVU")
print("=" * 60)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

print(f"Raw records: {len(raw_data)}")


# ============================================================
# 9. CLEANING
# ============================================================

cleaned_data = []

removed_count = 0
duplicate_count = 0

seen_hotel_ids = set()


for hotel in raw_data:

    hotel_id = hotel.get("hotel_id")
    name = clean_text(hotel.get("name"))

    # --------------------------------------------------------
    # Loại record thiếu khóa chính
    # --------------------------------------------------------

    if hotel_id is None or name is None:
        removed_count += 1
        continue

    # --------------------------------------------------------
    # Loại duplicate hotel_id
    # --------------------------------------------------------

    if hotel_id in seen_hotel_ids:
        duplicate_count += 1
        continue

    seen_hotel_ids.add(hotel_id)

    # --------------------------------------------------------
    # Giá
    # --------------------------------------------------------

    min_price = clean_price(hotel.get("min_price"))
    max_price = clean_price(hotel.get("max_price"))

    deal_price = clean_deal_price(
        hotel.get("deal_price")
    )

    # --------------------------------------------------------
    # Tiêu chí dữ liệu:
    #
    # Chỉ giữ hotel có thông tin min_price hoặc max_price.
    #
    # Raw vẫn giữ đầy đủ 1189 record.
    # --------------------------------------------------------

    if min_price is None and max_price is None:
        removed_count += 1
        continue

    # --------------------------------------------------------
    # Star rating
    # --------------------------------------------------------

    star_rating = hotel.get("star_rating")

    if star_rating is not None:
        try:
            star_rating = float(star_rating)
        except (ValueError, TypeError):
            star_rating = None

    # --------------------------------------------------------
    # Review score
    # --------------------------------------------------------

    review_score = hotel.get("review_score")

    if review_score is not None:
        try:
            review_score = float(review_score)
        except (ValueError, TypeError):
            review_score = None

    # --------------------------------------------------------
    # Review count
    # --------------------------------------------------------

    review_count = hotel.get("review_count")

    if review_count is not None:
        try:
            review_count = int(review_count)
        except (ValueError, TypeError):
            review_count = None

    # --------------------------------------------------------
    # Tạo record cleaned
    # --------------------------------------------------------

    cleaned_hotel = {
        "hotel_id": hotel_id,
        "hotel_code": clean_text(
            hotel.get("hotel_code")
        ),
        "name": name,

        "star_rating": star_rating,
        "review_score": review_score,
        "review_count": review_count,

        "min_price_vnd": min_price,
        "max_price_vnd": max_price,
        "deal_price_vnd": deal_price,

        "address": clean_text(
            hotel.get("address")
        ),

        "latitude": hotel.get("latitude"),
        "longitude": hotel.get("longitude"),

        "description": clean_list_text(
            hotel.get("description")
        ),

        "facilities": clean_facilities(
            hotel.get("facilities")
        ),

        "location_tags": clean_location_tags(
            hotel.get("location_tags")
        ),

        "hotel_url": clean_url(
            hotel.get("hotel_url")
        ),

        "source": clean_text(
            hotel.get("source")
        ),

        "crawl_date": clean_text(
            hotel.get("crawl_date")
        ),

        "check_in": clean_text(
            hotel.get("check_in")
        ),

        "check_out": clean_text(
            hotel.get("check_out")
        ),
    }

    cleaned_data.append(cleaned_hotel)


# ============================================================
# 10. TẠO THƯ MỤC OUTPUT
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 11. GHI CSV
# ============================================================

fieldnames = [
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
# 12. THỐNG KÊ KẾT QUẢ
# ============================================================

print()
print("=" * 60)
print("KET QUA CLEANING IVIVU")
print("=" * 60)

print(f"Raw records       : {len(raw_data)}")
print(f"Cleaned records   : {len(cleaned_data)}")
print(f"Removed records   : {removed_count}")
print(f"Duplicate removed : {duplicate_count}")

print()
print("Missing values:")

for field in fieldnames:

    missing = sum(
        1
        for row in cleaned_data
        if row.get(field) is None
        or row.get(field) == ""
    )

    print(
        f"{field:18}: {missing}"
    )

print()
print(f"Output file: {OUTPUT_FILE}")

print("=" * 60)
print("HOAN TAT CLEANING")
print("=" * 60)
