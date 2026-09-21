-- ============================================================
-- BIG DATA PROJECT - MYSQL QUERIES v2
-- Includes TGDD product_id
-- ============================================================

USE bigdata_project;

-- ============================================================
-- 1. TỔNG QUAN DỮ LIỆU
-- ============================================================

SELECT 'TGDĐ' AS dataset, COUNT(*) AS records FROM laptops
UNION ALL
SELECT 'iVIVU', COUNT(*) FROM hotels;

SELECT
    (SELECT COUNT(*) FROM laptops) +
    (SELECT COUNT(*) FROM hotels) AS total_records;

-- ============================================================
-- 2. KIỂM TRA ID NGUỒN
-- ============================================================

SELECT
    COUNT(*) AS total,
    COUNT(product_id) AS product_id_not_null,
    COUNT(DISTINCT product_id) AS unique_product_id
FROM laptops;

SELECT product_id, COUNT(*) AS duplicate_count
FROM laptops
GROUP BY product_id
HAVING COUNT(*) > 1;

SELECT
    MIN(product_id) AS min_product_id,
    MAX(product_id) AS max_product_id
FROM laptops;

SELECT
    COUNT(*) AS total,
    COUNT(hotel_id) AS hotel_id_not_null,
    COUNT(DISTINCT hotel_id) AS unique_hotel_id
FROM hotels;

-- ============================================================
-- 3. LAPTOP - THƯƠNG HIỆU
-- ============================================================

SELECT brand, COUNT(*) AS product_count
FROM laptops
GROUP BY brand
ORDER BY product_count DESC;

-- ============================================================
-- 4. LAPTOP - GIÁ
-- ============================================================

SELECT
    MIN(price_vnd) AS min_price,
    AVG(price_vnd) AS avg_price,
    MAX(price_vnd) AS max_price
FROM laptops;

SELECT
    product_id,
    name,
    brand,
    price_vnd
FROM laptops
ORDER BY price_vnd DESC
LIMIT 10;

SELECT
    product_id,
    name,
    brand,
    price_vnd
FROM laptops
ORDER BY price_vnd ASC
LIMIT 10;

-- ============================================================
-- 5. LAPTOP - RAM / STORAGE
-- ============================================================

SELECT ram_gb, COUNT(*) AS product_count
FROM laptops
GROUP BY ram_gb
ORDER BY ram_gb;

SELECT storage_gb, COUNT(*) AS product_count
FROM laptops
GROUP BY storage_gb
ORDER BY storage_gb;

-- ============================================================
-- 6. LAPTOP - RATING
-- ============================================================

SELECT
    rating,
    COUNT(*) AS product_count
FROM laptops
WHERE rating IS NOT NULL
GROUP BY rating
ORDER BY rating DESC;

SELECT
    product_id,
    name,
    rating,
    review_count
FROM laptops
WHERE rating IS NOT NULL
ORDER BY rating DESC, review_count DESC
LIMIT 10;

-- ============================================================
-- 7. LAPTOP - CRUD DEMO
-- ============================================================

-- SELECT
SELECT *
FROM laptops
WHERE product_id = 343122;

-- INSERT example - do not execute unless needed:
-- INSERT INTO laptops
-- (product_id, name, brand, price_vnd, url, source, crawl_date)
-- VALUES
-- (999999, 'Demo Laptop', 'Demo', 10000000,
--  'https://example.com/demo', 'demo', CURRENT_DATE);

-- UPDATE example - do not execute unless needed:
-- UPDATE laptops
-- SET price_vnd = 9999999
-- WHERE product_id = 999999;

-- DELETE example - do not execute unless needed:
-- DELETE FROM laptops
-- WHERE product_id = 999999;

-- ============================================================
-- 8. HOTEL - SAO
-- ============================================================

SELECT
    star_rating,
    COUNT(*) AS hotel_count
FROM hotels
GROUP BY star_rating
ORDER BY star_rating DESC;

-- ============================================================
-- 9. HOTEL - GIÁ
-- ============================================================

SELECT
    MIN(min_price_vnd) AS min_price,
    AVG(min_price_vnd) AS avg_min_price,
    MAX(min_price_vnd) AS max_price
FROM hotels;

SELECT
    hotel_id,
    name,
    star_rating,
    min_price_vnd,
    max_price_vnd
FROM hotels
ORDER BY min_price_vnd ASC
LIMIT 10;

SELECT
    hotel_id,
    name,
    star_rating,
    min_price_vnd,
    max_price_vnd
FROM hotels
ORDER BY min_price_vnd DESC
LIMIT 10;

-- ============================================================
-- 10. HOTEL - ĐÁNH GIÁ
-- ============================================================

SELECT
    hotel_id,
    name,
    star_rating,
    review_score,
    review_count
FROM hotels
ORDER BY review_score DESC, review_count DESC
LIMIT 10;

-- ============================================================
-- 11. HOTEL - DEAL PRICE
-- ============================================================

SELECT
    COUNT(*) AS total_hotels,
    COUNT(deal_price_vnd) AS hotels_with_deal
FROM hotels;

SELECT
    hotel_id,
    name,
    min_price_vnd,
    deal_price_vnd,
    (min_price_vnd - deal_price_vnd) AS saving_vnd
FROM hotels
WHERE deal_price_vnd IS NOT NULL
  AND deal_price_vnd > 0
ORDER BY saving_vnd DESC
LIMIT 10;

-- ============================================================
-- 12. DATA QUALITY
-- ============================================================

SELECT
    COUNT(*) AS total,
    SUM(price_vnd IS NULL) AS missing_price,
    SUM(name IS NULL OR name = '') AS missing_name,
    SUM(url IS NULL OR url = '') AS missing_url,
    SUM(product_id IS NULL) AS missing_product_id
FROM laptops;

SELECT
    COUNT(*) AS total,
    SUM(min_price_vnd IS NULL) AS missing_min_price,
    SUM(max_price_vnd IS NULL) AS missing_max_price,
    SUM(name IS NULL OR name = '') AS missing_name,
    SUM(hotel_id IS NULL) AS missing_hotel_id
FROM hotels;

-- ============================================================
-- 13. SUMMARY
-- ============================================================

SELECT
    COUNT(*) AS laptop_count,
    MIN(price_vnd) AS cheapest_laptop,
    MAX(price_vnd) AS most_expensive_laptop,
    AVG(price_vnd) AS average_laptop_price
FROM laptops;

SELECT
    COUNT(*) AS hotel_count,
    MIN(min_price_vnd) AS cheapest_hotel,
    MAX(min_price_vnd) AS highest_min_price,
    AVG(min_price_vnd) AS average_hotel_price
FROM hotels;
