-- ============================================================
-- BIG DATA PROJECT - MySQL DATA IMPORT
-- ============================================================

USE bigdata_project;

-- WARNING: clears existing rows before re-importing.
TRUNCATE TABLE laptops;
TRUNCATE TABLE hotels;

-- TGDD laptops
LOAD DATA INFILE '/var/lib/mysql-files/laptop_clean.csv'
INTO TABLE laptops
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    name, brand, price_vnd, @old_price_vnd, @discount_percent,
    @rating, @review_count, @screen_size_inch, cpu, gpu,
    @ram_gb, @storage_gb, @weight_kg, url, source, @crawl_date
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

-- iVIVU hotels
LOAD DATA INFILE '/var/lib/mysql-files/hotel_dalat_clean.csv'
INTO TABLE hotels
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    hotel_id, hotel_code, name, @star_rating, @review_score,
    @review_count, min_price_vnd, max_price_vnd, @deal_price_vnd,
    @address, @latitude, @longitude, @description, @facilities,
    @location_tags, hotel_url, source, @crawl_date, @check_in, @check_out
)
SET
    star_rating = NULLIF(@star_rating, ''),
    review_score = NULLIF(@review_score, ''),
    review_count = NULLIF(@review_count, ''),
    deal_price_vnd = NULLIF(@deal_price_vnd, ''),
    address = NULLIF(@address, ''),
    latitude = NULLIF(@latitude, ''),
    longitude = NULLIF(@longitude, ''),
    description = NULLIF(@description, ''),
    facilities = NULLIF(@facilities, ''),
    location_tags = NULLIF(@location_tags, ''),
    crawl_date = STR_TO_DATE(@crawl_date, '%Y-%m-%d'),
    check_in = STR_TO_DATE(@check_in, '%Y-%m-%d'),
    check_out = STR_TO_DATE(@check_out, '%Y-%m-%d');

-- Verification
SELECT 'laptops' AS table_name, COUNT(*) AS record_count FROM laptops
UNION ALL
SELECT 'hotels', COUNT(*) FROM hotels;
