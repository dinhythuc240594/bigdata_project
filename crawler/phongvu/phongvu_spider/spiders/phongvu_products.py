import json
import scrapy


class PhongvuProductsSpider(scrapy.Spider):
    name = "phongvu_products"
    allowed_domains = [
        "discovery.tekoapis.com",
    ]

    api_url = "https://discovery.tekoapis.com/api/v2/search-skus-v2"

    custom_settings = {
        "ROBOTSTXT_OBEY": False,

        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,

        "DOWNLOAD_DELAY": 1.0,

        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,

        "DOWNLOAD_TIMEOUT": 60,

        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "*/*",
            "Origin": "https://phongvu.vn",
            "Referer": "https://phongvu.vn/",
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/153.0.0.0 Safari/537.36"
            ),
            "accept-language": "vi",
            "content-type": "application/json",
        },

        "FEEDS": {
            "data/raw/phongvu/products_full.json": {
                "format": "json",
                "encoding": "utf-8",
                "indent": 2,
                "overwrite": True,
            }
        },

        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # SKU đã xuất ra
        self.seen_skus = set()

        # Thống kê
        self.category_count = 0
        self.page_count = 0
        self.product_count = 0
        self.duplicate_count = 0

    async def start(self):
        """
        Đọc toàn bộ category từ /tmp/phongvu_slugs.txt
        """

        with open(
            "/tmp/phongvu_slugs.txt",
            "r",
            encoding="utf-8"
        ) as f:

            slugs = [
                line.strip()
                for line in f
                if line.strip()
            ]

        # Loại duplicate slug nếu có
        slugs = sorted(set(slugs))

        self.logger.info(
            "TONG SO CATEGORY: %d",
            len(slugs)
        )

        for slug in slugs:

            self.category_count += 1

            yield scrapy.Request(
                url=self.api_url,
                method="POST",
                headers={
                    "Accept": "*/*",
                    "Origin": "https://phongvu.vn",
                    "Referer": "https://phongvu.vn/",
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/153.0.0.0 Safari/537.36"
                    ),
                    "accept-language": "vi",
                    "content-type": "application/json",
                    "meta_data": '{"start_at":1407}',
                },
                body=json.dumps({
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
                }),
                callback=self.parse_products,
                errback=self.errback_api,
                meta={
                    "slug": slug,
                    "page": 1,
                },
                dont_filter=True,
            )

    def parse_products(self, response):

        slug = response.meta["slug"]
        page = response.meta["page"]

        self.page_count += 1

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:

            self.logger.error(
                "JSON ERROR: %s page=%d",
                slug,
                page
            )

            return

        if response.status != 200:

            self.logger.error(
                "HTTP %d | %s | page=%d | %s",
                response.status,
                slug,
                page,
                response.text[:500]
            )

            return

        api_data = data.get("data") or {}

        products = api_data.get("products") or []

        total = api_data.get("total") or 0

        page_size = api_data.get("pageSize") or 40

        self.logger.info(
            "[%s] page=%d | products=%d | total=%s",
            slug,
            page,
            len(products),
            total
        )

        for product in products:

            sku = (
                product.get("sku")
                or product.get("sellerSku")
            )

            if not sku:
                self.logger.warning(
                    "PRODUCT KHONG CO SKU | %s",
                    slug
                )
                continue

            sku = str(sku)

            # =========================
            # DEDUPLICATE
            # =========================

            if sku in self.seen_skus:

                self.duplicate_count += 1

                continue

            self.seen_skus.add(sku)

            self.product_count += 1

            # =========================
            # LẤY THÔNG TIN SẢN PHẨM
            # =========================

            yield {
                "sku": sku,

                "product_id": product.get(
                    "productId"
                ),

                "seller_sku": product.get(
                    "sellerSku"
                ),

                "name": product.get(
                    "name"
                ),

                "brand": product.get(
                    "brandName"
                ),

                "supplier_retail_price": product.get(
                    "supplierRetailPrice"
                ),

                "price": product.get(
                    "latestPrice"
                ),

                "discount_amount": product.get(
                    "discountAmount"
                ),

                "discount_percent": product.get(
                    "discountPercent"
                ),

                "min_price": product.get(
                    "minLatestPrice"
                ),

                "max_price": product.get(
                    "maxLatestPrice"
                ),

                "url": product.get(
                    "canonicalUrl"
                ) or product.get(
                    "url"
                ),

                "categories": product.get(
                    "categories"
                ),

                # Category mà sản phẩm được crawl từ đó
                "crawl_category": slug,

                "source": "Phong Vu",
            }

        # =========================
        # PAGINATION
        # =========================

        next_page = page + 1

        if page * page_size < total:

            yield scrapy.Request(
                url=self.api_url,
                method="POST",
                headers={
                    "Accept": "*/*",
                    "Origin": "https://phongvu.vn",
                    "Referer": "https://phongvu.vn/",
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/153.0.0.0 Safari/537.36"
                    ),
                    "accept-language": "vi",
                    "content-type": "application/json",
                    "meta_data": '{"start_at":1407}',
                },
                body=json.dumps({
                    "terminalId": 4,
                    "page": next_page,
                    "pageSize": 40,
                    "slug": slug,
                    "filter": {},
                    "sorting": {
                        "sort": "SORT_BY_CREATED_AT",
                        "order": "ORDER_BY_DESCENDING"
                    },
                    "returnFilterable": [],
                    "isNeedFeaturedProducts": True
                }),
                callback=self.parse_products,
                errback=self.errback_api,
                meta={
                    "slug": slug,
                    "page": next_page,
                },
                dont_filter=True,
            )

    def errback_api(self, failure):

        request = failure.request

        self.logger.error(
            "REQUEST ERROR | %s | page=%s | %s",
            request.meta.get("slug"),
            request.meta.get("page"),
            failure.value,
        )

    def closed(self, reason):

        self.logger.info("=" * 70)
        self.logger.info("PHONG VU CRAWL FINISHED")
        self.logger.info("REASON: %s", reason)
        self.logger.info("CATEGORY: %d", self.category_count)
        self.logger.info("PAGES: %d", self.page_count)
        self.logger.info("UNIQUE PRODUCTS: %d", self.product_count)
        self.logger.info("DUPLICATES: %d", self.duplicate_count)
        self.logger.info("=" * 70)