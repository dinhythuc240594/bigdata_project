import json
import requests

url = "https://discovery.tekoapis.com/api/v2/search-skus-v2"

headers = {
    "Accept": "*/*",
    "Origin": "https://phongvu.vn",
    "Referer": "https://phongvu.vn/",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/153.0.0.0 Safari/537.36",
    "accept-language": "vi",
    "content-type": "application/json",
    "meta_data": '{"start_at":149482}',
}

payload = {
    "terminalId": 4,
    "page": 1,
    "pageSize": 40,
    "slug": "/c/pc-van-phong",
    "filter": {},
    "sorting": {
        "sort": "SORT_BY_CREATED_AT",
        "order": "ORDER_BY_DESCENDING"
    },
    "returnFilterable": [],
    "isNeedFeaturedProducts": True
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=30
)

print("STATUS:", response.status_code)
print("CONTENT-TYPE:", response.headers.get("content-type"))
print()

data = response.json()

print("TOP-LEVEL KEYS:")
print(list(data.keys()))
print()

print("DATA KEYS:")
if isinstance(data.get("data"), dict):
    print(list(data["data"].keys()))
else:
    print(type(data.get("data")))

print()
print("FULL RESPONSE:")
print(json.dumps(data, ensure_ascii=False, indent=2)[:20000])
