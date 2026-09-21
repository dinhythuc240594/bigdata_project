import requests
import json

url = "https://discovery.tekoapis.com/api/v2/search-skus-v2"

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

payload = {
    "terminalId": 4,
    "page": 1,
    "pageSize": 40,
    #"slug": "/c/pc-van-phong",
    "slug": "/c/may-tinh-de-ban",
    "filter": {},
    "sorting": {
        "sort": "SORT_BY_CREATED_AT",
        "order": "ORDER_BY_DESCENDING"
    },
    "returnFilterable": [],
    "isNeedFeaturedProducts": True
}

r = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=30
)

print("STATUS:", r.status_code)

data = r.json()

# Lưu toàn bộ response
with open("/tmp/pv.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Đã lưu response vào /tmp/pv.json")

print("MESSAGE:", data.get("message"))

api_data = data.get("data") or {}

print("TOTAL:", api_data.get("total"))
print("PAGE:", api_data.get("page"))
print("PAGE SIZE:", api_data.get("pageSize"))

products = api_data.get("products") or []

print("PRODUCTS:", len(products))

if products:
    print("\nFIRST PRODUCT:")
    print(json.dumps(
        products[0],
        ensure_ascii=False,
        indent=2
    ))
