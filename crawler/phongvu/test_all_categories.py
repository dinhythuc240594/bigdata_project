import requests
import time

URL = "https://discovery.tekoapis.com/api/v2/search-skus-v2"

headers = {
    "Accept": "*/*",
    "Origin": "https://phongvu.vn",
    "Referer": "https://phongvu.vn/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    ),
    "accept-language": "vi",
    "content-type": "application/json",
    "meta_data": '{"start_at":1407}',
}

with open("/tmp/phongvu_slugs.txt", encoding="utf-8") as f:
    slugs = [x.strip() for x in f if x.strip()]

results = []

for i, slug in enumerate(slugs, 1):

    payload = {
        "terminalId": 4,
        "page": 1,
        "pageSize": 40,
        "slug": slug,
        "filter": {},
        "sorting": {
            "sort": "SORT_BY_CREATED_AT",
            "order": "ORDER_BY_DESCENDING"
        },
        "returnFilterable": [],
        "isNeedFeaturedProducts": True
    }

    try:
        r = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        data = r.json()
        d = data.get("data") or {}

        total = d.get("total") or 0
        products = d.get("products") or []

        results.append((slug, total))

        print(
            f"[{i:03d}/{len(slugs):03d}] "
            f"{slug:<45} TOTAL={total}"
        )

    except Exception as e:
        print(
            f"[{i:03d}/{len(slugs):03d}] "
            f"{slug:<45} ERROR={e}"
        )

    time.sleep(0.3)

print("\n========== CATEGORY NHIỀU SẢN PHẨM ==========")

for slug, total in sorted(
    results,
    key=lambda x: x[1],
    reverse=True
):
    if total > 0:
        print(f"{total:6d}  {slug}")
