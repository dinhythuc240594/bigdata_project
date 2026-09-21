import json
import scrapy


class IvivuHotelSpider(scrapy.Spider):
    name = "ivivu_hotel"
    allowed_domains = ["apiportal.ivivu.com"]

    api_url = (
        "https://apiportal.ivivu.com/"
        "web_prot/ms01/api/SearchFilters/SearchHotelList"
    )

    region_id = 114217

    check_in = "2026-09-23"
    check_out = "2026-09-24"

    page_size = 15

    # TEST TRƯỚC 2 PAGE = 30 KHÁCH SẠN
    max_pages = 80

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    async def start(self):
        self.logger.info("=== BAT DAU CRAWL IVIVU ===")
        self.logger.info("Gui request API page 1")

        yield self.make_request(1)

    def make_request(self, page_index):

        payload = {
            "regionId": self.region_id,
            "checkInDate": self.check_in,
            "checkOutDate": self.check_out,
            "roomPicker": {
                "adultNumber": 2,
                "childNumber": 0,
                "roomNumber": 1,
                "childAges": [],
                "type": "[Layout] Set Room Picker",
            },
            "pageIndex": page_index,
            "pageSize": self.page_size,
            "args": {},
            "sortOrder": 5,
        }

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://www.ivivu.com",
            "Referer": "https://www.ivivu.com/",
            "X-Client-Source": "IVIVU_WEB",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/152.0.0.0 Safari/537.36"
            ),
        }

        return scrapy.Request(
            url=self.api_url,
            method="POST",
            headers=headers,
            body=json.dumps(payload),
            callback=self.parse,
            cb_kwargs={"page_index": page_index},
            dont_filter=True,
        )

    def parse(self, response, page_index):

        self.logger.info(
            f"API response page {page_index}: "
            f"HTTP {response.status}"
        )

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            self.logger.error(
                f"Khong parse duoc JSON page {page_index}: {e}"
            )
            self.logger.error(
                f"Response: {response.text[:500]}"
            )
            return

        if not data.get("success"):
            self.logger.error(
                f"API loi tai page {page_index}: "
                f"{data.get('error')}"
            )
            return

        api_data = data.get("data", {})

        hotels = api_data.get("list", [])
        total = api_data.get("total", 0)

        self.logger.info(
            f"Page {page_index}: "
            f"{len(hotels)} hotels | "
            f"Total API: {total}"
        )

        for hotel in hotels:

            rating = hotel.get("rating")

            if rating is not None:
                try:
                    star_rating = float(rating) / 10
                except (ValueError, TypeError):
                    star_rating = None
            else:
                star_rating = None

            yield {
                "hotel_id": hotel.get("hotelId"),
                "hotel_code": hotel.get("hotelCode"),
                "name": hotel.get("hotelName"),

                "star_rating": star_rating,

                "review_score": self.to_float(
                    hotel.get("point")
                ),

                "review_count": hotel.get("reviewCount"),

                "min_price": hotel.get("minPrice"),
                "max_price": hotel.get("maxPrice"),
                "deal_price": hotel.get("dealPrice"),

                "address": hotel.get("address"),

                "latitude": hotel.get("lat"),
                "longitude": hotel.get("lon"),

                "description": hotel.get("description"),
                "facilities": hotel.get("facilities"),
                "location_tags": hotel.get("locationTags"),

                "hotel_url": hotel.get("hotelLink"),

                "source": "iVIVU",

                "crawl_date": "2026-09-20",

                "check_in": self.check_in,
                "check_out": self.check_out,
            }

        # Sang page tiep theo
        if page_index < self.max_pages:

            next_page = page_index + 1

            self.logger.info(
                f"Chuan bi crawl page {next_page}"
            )

            yield self.make_request(next_page)

    @staticmethod
    def to_float(value):

        try:
            if value is None:
                return None

            return float(
                str(value).replace(",", ".")
            )

        except (ValueError, TypeError):
            return None
