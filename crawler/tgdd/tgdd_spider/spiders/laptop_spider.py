import scrapy
import json
import re
from datetime import date


class LaptopSpider(scrapy.Spider):
    name = "laptop_spider"
    allowed_domains = ["thegioididong.com"]

    start_urls = [
        "https://www.thegioididong.com/laptop"
    ]

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    # =========================================================
    # 1. TRANG LAPTOP BAN ĐẦU
    # =========================================================

    def parse(self, response):

        links = response.css(
            'a[href^="/laptop/"]::attr(href)'
        ).getall()

        links = list(dict.fromkeys(links))

        self.logger.info(
            "Trang đầu: tìm thấy %s link laptop",
            len(links)
        )

        for href in links:

            yield scrapy.Request(
                response.urljoin(href),
                callback=self.parse_product
            )

        # Bắt đầu pagination
        yield self.request_next_page(1)

    # =========================================================
    # 2. REQUEST FILTERPRODUCTBOX
    # =========================================================

    def request_next_page(self, pi):

        url = (
            "https://www.thegioididong.com/"
            "Category/FilterProductBox"
        )

        request_url = (
            f"{url}?c=44&o=13&pi={pi}"
        )

        data = {
            "IsParentCate": "False",
            "IsShowCompare": "True",
            "prevent": "true"
        }

        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type":
                "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent":
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/152.0.0.0 Safari/537.36",
        }

        self.logger.info(
            ">>> Gửi POST FilterProductBox pi=%s",
            pi
        )

        return scrapy.FormRequest(
            url=request_url,
            method="POST",
            formdata=data,
            headers=headers,
            callback=self.parse_more_products,
            cb_kwargs={"pi": pi},
        )

    # =========================================================
    # 3. XỬ LÝ JSON TRẢ VỀ
    # =========================================================

    def parse_more_products(self, response, pi):

        self.logger.info(
            "<<< FilterProductBox pi=%s | status=%s | length=%s",
            pi,
            response.status,
            len(response.text)
        )

        try:
            result = json.loads(response.text)

        except json.JSONDecodeError:

            self.logger.error(
                "Không parse được JSON tại pi=%s",
                pi
            )

            return

        total = result.get("total")

        html = result.get(
            "listproducts",
            ""
        )

        self.logger.info(
            "pi=%s | total=%s | HTML=%s ký tự",
            pi,
            total,
            len(html)
        )

        if not html:

            self.logger.info(
                "Đã hết sản phẩm tại pi=%s",
                pi
            )

            return

        selector = scrapy.Selector(
            text=html
        )

        links = selector.css(
            'a[href^="/laptop/"]::attr(href)'
        ).getall()

        links = list(dict.fromkeys(links))

        self.logger.info(
            "pi=%s | tìm thấy %s laptop",
            pi,
            len(links)
        )

        if not links:

            self.logger.info(
                "Không còn laptop tại pi=%s",
                pi
            )

            return

        for href in links:

            yield scrapy.Request(
                response.urljoin(href),
                callback=self.parse_product
            )

        # Tiếp tục phân trang cho đến khi API không còn sản phẩm
        next_pi = pi + 1
        yield self.request_next_page(next_pi)

    # =========================================================
    # 4. LẤY THÔNG TIN CHI TIẾT LAPTOP
    # =========================================================

    def parse_product(self, response):
        product_id = response.xpath(
            '//section[contains(@class, "detailv2")]/@data-id'
        ).get()

        product_code = response.xpath(
            '//*[@data-proId]/@data-proId'
        ).get()

        if not product_code:
            product_code = response.xpath(
                '//*[@data-proCode]/@data-proCode'
            ).get()
        product = None

        scripts = response.css(
            'script[type="application/ld+json"]::text'
        ).getall()

        for script in scripts:

            try:

                data = json.loads(script)

                if isinstance(data, dict):

                    if data.get("@type") == "Product":

                        product = data
                        break

            except Exception:
                continue

        if not product:

            self.logger.warning(
                "Không tìm thấy Product JSON-LD: %s",
                response.url
            )

            return

        # =====================================================
        # SPECS
        # =====================================================

        specs = {}

        for item in product.get(
            "additionalProperty",
            []
        ):

            name = item.get("name")
            value = item.get("value")

            if name:

                specs[name] = value

        # =====================================================
        # CLEAN HTML
        # =====================================================

        def clean_html(value):

            if not value:
                return None

            value = re.sub(
                r"<[^>]+>",
                "",
                value
            )

            return value.strip()

        # =====================================================
        # BRAND
        # =====================================================

        brand = product.get("brand")

        if isinstance(brand, dict):

            brand = brand.get("name")

        if isinstance(brand, list):

            brand = (
                brand[0]
                if brand
                else None
            )

        # =====================================================
        # RATING
        # =====================================================

        rating_data = product.get("aggregateRating") or {}

        rating = rating_data.get("ratingValue")

        review_count = rating_data.get("reviewcount")

        # =====================================================
        # PRICE
        # =====================================================

        def parse_price(text):

            if not text:
                return None

            text = (
                text
                .replace("₫", "")
                .replace(".", "")
                .replace(",", "")
                .strip()
            )

            try:

                return float(text)

            except ValueError:

                return None

        price_text = response.css(
            ".box-price-present::text"
        ).get()

        price = parse_price(
            price_text
        )

        # Fallback JSON-LD
        if price is None:

            offers = product.get(
                "offers",
                {}
            )

            price = offers.get(
                "price"
            )

        # =====================================================
        # OLD PRICE
        # =====================================================

        old_price_text = response.css(
            ".box-price-old::text"
        ).get()

        old_price = parse_price(
            old_price_text
        )

        # =====================================================
        # DISCOUNT
        # =====================================================

        discount_text = response.css(
            ".box-price-percent::text"
        ).get()

        discount = None

        if discount_text:

            match = re.search(
                r"-?\d+",
                discount_text
            )

            if match:

                discount = int(
                    match.group()
                )

        # Tự tính discount nếu cần
        if (
            discount is None
            and price is not None
            and old_price is not None
            and old_price > 0
            and price < old_price
        ):

            discount = round(
                (price - old_price)
                / old_price
                * 100
            )

        # =====================================================
        # THÔNG SỐ
        # =====================================================

        cpu = clean_html(
            specs.get("Công nghệ CPU")
        )

        gpu = clean_html(
            specs.get("Card màn hình")
        )

        ram = specs.get("RAM")

        storage = specs.get(
            "Ổ cứng"
        )

        screen_size = specs.get(
            "Kích thước màn hình"
        )

        # =====================================================
        # WEIGHT
        # =====================================================

        size_info = specs.get(
            "Kích thước"
        )

        weight = None

        if size_info:

            match = re.search(
                r"([\d.,]+)\s*kg",
                size_info
            )

            if match:

                weight = match.group(1)

        # =====================================================
        # OUTPUT
        # =====================================================

        yield {
            "product_id":
                int(product_id) if product_id else None,

            "product_code":
                product_code,
            "name":
                product.get("name"),

            "brand":
                brand,

            "price":
                price,

            "old_price":
                old_price,

            "discount":
                discount,

            "rating":
                rating,

            "review_count":
                review_count,

            "sold_count":
                None,

            "screen_size":
                screen_size,

            "cpu":
                cpu,

            "gpu":
                gpu,

            "ram":
                ram,

            "storage":
                storage,

            "weight":
                weight,

            "url":
                response.url,

            "source":
                "thegioididong",

            "crawl_date":
                str(date.today())
        }