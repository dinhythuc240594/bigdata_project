import scrapy
import json
import re
from datetime import date


class ProductSpider(scrapy.Spider):
    name = "product_spider"
    allowed_domains = ["thegioididong.com"]

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 2,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    # =========================================================
    # CẤU HÌNH 3 CATEGORY
    # =========================================================

    CATEGORIES = {
        "laptop": {
            "url": "https://www.thegioididong.com/laptop",
            "category_id": 44,
            "prefix": "/laptop/",
            "output": "data/raw/tgdd/laptop_full_new.json",
        },

        "keyboard": {
            "url": "https://www.thegioididong.com/ban-phim",
            "category_id": 4547,
            "prefix": "/ban-phim/",
            "output": "data/raw/tgdd/keyboard_full.json",
        },

        "monitor": {
            "url": "https://www.thegioididong.com/man-hinh-may-tinh",
            "category_id": 5697,
            "prefix": "/man-hinh-may-tinh/",
            "output": "data/raw/tgdd/monitor_full.json",
        },
    }

    # =========================================================
    # START
    # =========================================================

    async def start(self):

        category = getattr(
            self,
            "crawl_category",
            "laptop"
        )

        if category not in self.CATEGORIES:

            raise ValueError(
                f"Category không hợp lệ: {category}. "
                f"Chọn: {list(self.CATEGORIES.keys())}"
            )

        config = self.CATEGORIES[category]

        self.current_category = category

        self.logger.info(
            "================================================="
        )

        self.logger.info(
            "BẮT ĐẦU CATEGORY: %s",
            category.upper()
        )

        self.logger.info(
            "CATEGORY ID: %s",
            config["category_id"]
        )

        self.logger.info(
            "URL: %s",
            config["url"]
        )

        self.logger.info(
            "================================================="
        )

        yield scrapy.Request(
            config["url"],
            callback=self.parse_category,
            meta={
                "category": category
            }
        )

    # =========================================================
    # TRANG CATEGORY BAN ĐẦU
    # =========================================================
    def parse_category(self, response):

        category = response.meta["category"]
        config = self.CATEGORIES[category]

        self.logger.info(
            "================================================="
        )

        self.logger.info(
            "CATEGORY: %s",
            category
        )

        self.logger.info(
            "URL: %s",
            response.url
        )

        self.logger.info(
            "================================================="
        )

        # -----------------------------------------------------
        # Tìm link sản phẩm trên trang category
        # -----------------------------------------------------

        prefix = config["prefix"]

        links = response.css(
            f'a[href^="{prefix}"]::attr(href)'
        ).getall()

        # Loại bỏ link trùng
        links = list(dict.fromkeys(links))

        self.logger.info(
            "Tìm thấy %s link sản phẩm category %s",
            len(links),
            category
        )

        # -----------------------------------------------------
        # Gửi request tới từng sản phẩm
        # -----------------------------------------------------

        for href in links:

            yield scrapy.Request(
                response.urljoin(href),
                callback=self.parse_product,
                meta={
                    "category": category
                }
            )

        # -----------------------------------------------------
        # Bật pagination
        # -----------------------------------------------------
        self.logger.info(
            "CATEGORY %s: chỉ test trang đầu, chưa bật pagination",
            category
        )

        yield self.request_next_page(category, 1)
    # =========================================================
    # FILTER PRODUCT BOX
    # =========================================================

    def request_next_page(self, category, pi):

        config = self.CATEGORIES[category]

        category_id = config["category_id"]

        if category_id is None:

            self.logger.warning(
                "CATEGORY %s chưa có category_id",
                category
            )

            return

        url = (
            "https://www.thegioididong.com/"
            "Category/FilterProductBox"
        )

        request_url = (
            f"{url}?c={category_id}&o=13&pi={pi}"
        )

        data = {
            "IsParentCate": "False",
            "IsShowCompare": "True",
            "prevent": "true"
        }

        headers = {

            "Accept": "*/*",

            "Accept-Language":
                "en-US,en;q=0.9",

            "Content-Type":
                "application/x-www-form-urlencoded; charset=UTF-8",

            "User-Agent":
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/152.0.0.0 Safari/537.36",
        }

        self.logger.info(
            ">>> %s | POST FilterProductBox | pi=%s",
            category,
            pi
        )

        return scrapy.FormRequest(
            url=request_url,
            method="POST",
            formdata=data,
            headers=headers,
            callback=self.parse_more_products,
            cb_kwargs={
                "category": category,
                "pi": pi
            }
        )

    # =========================================================
    # XỬ LÝ PAGINATION
    # =========================================================

    def parse_more_products(
        self,
        response,
        category,
        pi
    ):

        self.logger.info(
            "<<< %s | pi=%s | status=%s | length=%s",
            category,
            pi,
            response.status,
            len(response.text)
        )

        try:
            result = json.loads(response.text)

        except json.JSONDecodeError:
            self.logger.error(
                "Không parse được JSON: %s pi=%s",
                category,
                pi
            )
            return

        total = result.get("total")

        html = result.get(
            "listproducts",
            ""
        )

        self.logger.info(
            "%s | pi=%s | total=%s | HTML=%s",
            category,
            pi,
            total,
            len(html)
        )

        if not html:
            self.logger.info(
                "%s: hết sản phẩm tại pi=%s",
                category,
                pi
            )
            return

        selector = scrapy.Selector(
            text=html
        )

        # -----------------------------------------------------
        # Lấy cấu hình category
        # -----------------------------------------------------

        config = self.CATEGORIES[category]

        prefix = config["prefix"]

        # -----------------------------------------------------
        # Tìm link sản phẩm
        # -----------------------------------------------------

        links = selector.css(
            f'a[href^="{prefix}"]::attr(href)'
        ).getall()

        # Loại bỏ trùng
        links = list(dict.fromkeys(links))

        self.logger.info(
            "%s | pi=%s | tìm thấy %s link sản phẩm",
            category,
            pi,
            len(links)
        )

        # -----------------------------------------------------
        # Nếu không còn sản phẩm
        # -----------------------------------------------------

        if not links:
            self.logger.info(
                "%s: không tìm thấy sản phẩm tại pi=%s",
                category,
                pi
            )
            return

        # -----------------------------------------------------
        # Request từng trang sản phẩm
        # -----------------------------------------------------

        for href in links:

            yield scrapy.Request(
                response.urljoin(href),
                callback=self.parse_product,
                meta={
                    "category": category
                }
            )

        # -----------------------------------------------------
        # Sang trang tiếp theo
        # -----------------------------------------------------

        next_pi = pi + 1

        yield self.request_next_page(
            category,
            next_pi
        )

    # =========================================================
    # PRODUCT DETAIL
    # =========================================================

    def parse_product(self, response):

        category = response.meta.get(
            "category"
        )

        # =====================================================
        # PRODUCT ID
        # =====================================================

        product_id = response.xpath(
            '//section[contains(@class, "detailv2")]/@data-id'
        ).get()

        # =====================================================
        # PRODUCT CODE
        # =====================================================

        product_code = response.xpath(
            '//*[@data-proId]/@data-proId'
        ).get()

        if not product_code:

            product_code = response.xpath(
                '//*[@data-proCode]/@data-proCode'
            ).get()

        # =====================================================
        # JSON-LD PRODUCT
        # =====================================================

        product = None

        scripts = response.css(
            'script[type="application/ld+json"]::text'
        ).getall()

        for script in scripts:

            try:

                data = json.loads(
                    script
                )

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
                str(value)
            )

            return value.strip()

        # =====================================================
        # BRAND
        # =====================================================

        brand = product.get(
            "brand"
        )

        if isinstance(
            brand,
            dict
        ):

            brand = brand.get(
                "name"
            )

        if isinstance(
            brand,
            list
        ):

            brand = (
                brand[0]
                if brand
                else None
            )

        # =====================================================
        # RATING
        # =====================================================

        rating_data = (
            product.get(
                "aggregateRating"
            )
            or {}
        )

        rating = rating_data.get(
            "ratingValue"
        )

        review_count = rating_data.get(
            "reviewcount"
        )

        # =====================================================
        # PRICE
        # =====================================================

        def parse_price(text):

            if not text:

                return None

            text = (
                str(text)
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

        # =====================================================
        # LAPTOP SPECS
        # =====================================================

        cpu = clean_html(
            specs.get(
                "Công nghệ CPU"
            )
        )

        gpu = clean_html(
            specs.get(
                "Card màn hình"
            )
        )

        ram = specs.get(
            "RAM"
        )

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
                str(size_info)
            )

            if match:

                weight = match.group(1)

        # =====================================================
        # CATEGORY-SPECIFIC FIELDS
        # =====================================================

        connection_type = None
        keyboard_type = None
        switch_type = None
        layout = None
        backlight = None

        resolution = None
        refresh_rate = None
        panel_type = None
        response_time = None

        # -----------------------------------------------------
        # KEYBOARD
        # -----------------------------------------------------

        if category == "keyboard":

            connection_type = (
                specs.get("Kết nối")
                or specs.get("Kết nối không dây")
            )

            keyboard_type = (
                specs.get("Kiểu bàn phím")
                or specs.get("Loại bàn phím")
            )

            switch_type = (
                specs.get("Loại switch")
                or specs.get("Switch")
            )

            layout = (
                specs.get("Kiểu bố trí")
                or specs.get("Layout")
            )

            backlight = (
                specs.get("Đèn nền")
                or specs.get("Đèn bàn phím")
            )

        # -----------------------------------------------------
        # MONITOR
        # -----------------------------------------------------

        if category == "monitor":

            resolution = (
                specs.get("Độ phân giải")
            )

            refresh_rate = (
                specs.get("Tần số quét")
            )

            panel_type = (
                specs.get("Tấm nền")
                or specs.get("Loại màn hình")
            )

            response_time = (
                specs.get("Thời gian đáp ứng")
            )

        # =====================================================
        # OUTPUT
        # =====================================================

        yield {

            # -------------------------------------------------
            # COMMON
            # -------------------------------------------------

            "product_id":
                int(product_id)
                if product_id
                else None,

            "product_code":
                product_code,

            "name":
                product.get("name"),

            "brand":
                brand,

            "category":
                category,

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

            "url":
                response.url,

            "source":
                "thegioididong",

            "crawl_date":
                str(date.today()),

            # -------------------------------------------------
            # LAPTOP
            # -------------------------------------------------

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

            # -------------------------------------------------
            # KEYBOARD
            # -------------------------------------------------

            "connection_type":
                connection_type,

            "keyboard_type":
                keyboard_type,

            "switch_type":
                switch_type,

            "layout":
                layout,

            "backlight":
                backlight,

            # -------------------------------------------------
            # MONITOR
            # -------------------------------------------------

            "resolution":
                resolution,

            "refresh_rate":
                refresh_rate,

            "panel_type":
                panel_type,

            "response_time":
                response_time,
        }
