-- ============================================================
-- BIG DATA PROJECT
-- Import cleaned CSV into MySQL
-- ============================================================

USE bigdata_project;


-- ============================================================
-- 1. LAPTOP COMMON
-- ============================================================

LOAD DATA INFILE
'/var/lib/mysql-files/laptop_products_common.csv'
INTO TABLE laptop_products_common
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    record_id,
    product_id,
    sku,
    name,
    brand,
    category,
    price_vnd,
    old_price_vnd,
    discount_amount_vnd,
    discount_percent,
    rating,
    review_count,
    url,
    source,
    crawl_date
);


-- ============================================================
-- 2. LAPTOP SPECS
-- ============================================================

LOAD DATA INFILE
'/var/lib/mysql-files/laptop_specs.csv'
INTO TABLE laptop_specs
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    record_id,
    product_id,
    sku,
    cpu,
    ram_gb,
    storage_gb,
    gpu,
    screen_size_inch,
    weight_kg
);


-- ============================================================
-- 3. KEYBOARD COMMON
-- ============================================================

LOAD DATA INFILE
'/var/lib/mysql-files/keyboard_products_common.csv'
INTO TABLE keyboard_products_common
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    record_id,
    product_id,
    sku,
    name,
    brand,
    category,
    price_vnd,
    old_price_vnd,
    discount_amount_vnd,
    discount_percent,
    rating,
    review_count,
    url,
    source,
    crawl_date
);


-- ============================================================
-- 4. KEYBOARD SPECS
-- ============================================================

LOAD DATA INFILE
'/var/lib/mysql-files/keyboard_specs.csv'
INTO TABLE keyboard_specs
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    record_id,
    product_id,
    sku,
    connection_type,
    keyboard_type,
    switch_type,
    layout,
    backlight
);


-- ============================================================
-- 5. MONITOR COMMON
-- ============================================================

LOAD DATA INFILE
'/var/lib/mysql-files/monitor_products_common.csv'
INTO TABLE monitor_products_common
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    record_id,
    product_id,
    sku,
    name,
    brand,
    category,
    price_vnd,
    old_price_vnd,
    discount_amount_vnd,
    discount_percent,
    rating,
    review_count,
    url,
    source,
    crawl_date
);


-- ============================================================
-- 6. MONITOR SPECS
-- ============================================================

LOAD DATA INFILE
'/var/lib/mysql-files/monitor_specs.csv'
INTO TABLE monitor_specs
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    record_id,
    product_id,
    sku,
    screen_size_inch,
    resolution,
    refresh_rate_hz,
    panel_type,
    response_time_ms
);


-- ============================================================
-- VERIFICATION
-- ============================================================

SELECT 'laptop_products_common' AS table_name,
       COUNT(*) AS total
FROM laptop_products_common

UNION ALL

SELECT 'laptop_specs',
       COUNT(*)
FROM laptop_specs

UNION ALL

SELECT 'keyboard_products_common',
       COUNT(*)
FROM keyboard_products_common

UNION ALL

SELECT 'keyboard_specs',
       COUNT(*)
FROM keyboard_specs

UNION ALL

SELECT 'monitor_products_common',
       COUNT(*)
FROM monitor_products_common

UNION ALL

SELECT 'monitor_specs',
       COUNT(*)
FROM monitor_specs;

