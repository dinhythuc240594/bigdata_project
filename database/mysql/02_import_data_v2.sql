-- ============================================================
-- BIG DATA PROJECT - MYSQL DATA IMPORT v2
-- Updated: TGDD product_id included
-- ============================================================

USE bigdata_project;

-- WARNING:
-- This script clears existing rows before re-importing.
TRUNCATE TABLE laptops;
TRUNCATE TABLE hotels;

-- ============================================================
-- 1. TGDD LAPTOPS
-- Expected current cleaned dataset: 418 records
-- CSV columns:
-- product_id, name, brand, price_vnd, old_price_vnd,
-- discount_percent, rating, review_count, screen_size_inch,
-- cpu, gpu, ram_gb, storage_gb, weight_kg, url, source, crawl_date
-- ============================================================

LOAD DATA INFILE '/var/lib/mysql-files/laptop_clean.csv'
INTO TABLE laptops
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    product_id,
    name,
    brand,
    price_vnd,
    @old_price_vnd,
    @discount_percent,
    @rating,
    @review_count,
    @screen_size_inch,
    cpu,
    gpu,
    @ram_gb,
    @storage_gb,
    @weight_kg,
    url,
    source,
    @crawl_date
)
SET
    old_price_vnd = NULLIF(@old_price_vnd, ''),
    discount_percent = NULLIF(@discount_percent, ''),
    rating = NULLIF(@rating, ''),
    review_count = NULLIF(@review_count, ''),
    screen_size_inch = NULLIF(@screen_size_inch, ''),
    ram_gb = NULLIF(@ram_gb, ''),
    storage_gb = NULLIF(@storage_gb, ''),
    weight_kg = NULLIF(@weight_kg, ''),
    crawl_date = STR_TO_DATE(@crawl_date, '%Y-%m-%d');

-- ============================================================
-- 2. IVIVU HOTELS
-- Expected current cleaned dataset: 655 records
-- ============================================================

LOAD DATA INFILE '/var/lib/mysql-files/hotel_dalat_clean.csv'
INTO TABLE hotels
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    hotel_id,
    hotel_code,
    name,
    star_rating,
    review_score,
    review_count,
    min_price_vnd,
    max_price_vnd,
    @deal_price_vnd,
    address,
    latitude,
    longitude,
    description,
    facilities,
    location_tags,
    hotel_url,
    source,
    @crawl_date,
    @check_in,
    @check_out
)
SET
    deal_price_vnd = NULLIF(@deal_price_vnd, ''),
    crawl_date = STR_TO_DATE(@crawl_date, '%Y-%m-%d'),
    check_in = STR_TO_DATE(@check_in, '%Y-%m-%d'),
    check_out = STR_TO_DATE(@check_out, '%Y-%m-%d');

-- ============================================================
-- 3. VERIFICATION
-- ============================================================

SELECT 'TGDĐ' AS dataset, COUNT(*) AS records FROM laptops
UNION ALL
SELECT 'iVIVU', COUNT(*) FROM hotels;

SELECT
    COUNT(*) AS total,
    COUNT(product_id) AS product_id_not_null,
    COUNT(DISTINCT product_id) AS unique_product_id
FROM laptops;

SELECT
    COUNT(*) AS total,
    COUNT(hotel_id) AS hotel_id_not_null,
    COUNT(DISTINCT hotel_id) AS unique_hotel_id
FROM hotels;
