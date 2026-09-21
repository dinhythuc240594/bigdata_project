import requests

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

slugs = [
    "/c/may-tinh-de-ban",
    "/c/pc-van-phong",
]

for slug in slugs:

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

        print("=" * 70)
        print("SLUG:", slug)
        print("HTTP:", r.status_code)
        print("CODE:", data.get("code"))
        print("MESSAGE:", data.get("message"))
        print("TOTAL:", d.get("total"))
        print("PRODUCTS:", len(d.get("products") or []))

        breadcrumbs = d.get("breadcrumbs") or []

        print("BREADCRUMBS:")
        for b in breadcrumbs:
            print("  ", b.get("label"), "=>", b.get("url"))

    except Exception as e:
        print("=" * 70)
        print("ERROR:", slug)
        print(e)
