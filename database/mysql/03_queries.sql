USE bigdata_project;

-- ============================================================
-- 03_queries.sql
-- Truy vấn, thống kê, JOIN và CRUD
-- Dataset: Thế Giới Di Động + Phong Vũ
-- ============================================================


-- ============================================================
-- 1. KIỂM TRA TỔNG QUAN DỮ LIỆU
-- ============================================================

-- 1.1. Đếm số sản phẩm từng loại
SELECT 'Laptop' AS category, COUNT(*) AS total
FROM laptop_products_common

UNION ALL

SELECT 'Keyboard' AS category, COUNT(*) AS total
FROM keyboard_products_common

UNION ALL

SELECT 'Monitor' AS category, COUNT(*) AS total
FROM monitor_products_common;


-- 1.2. Phân bố nguồn dữ liệu Laptop
SELECT source, COUNT(*) AS total
FROM laptop_products_common
GROUP BY source
ORDER BY total DESC;


-- 1.3. Phân bố nguồn dữ liệu Keyboard
SELECT source, COUNT(*) AS total
FROM keyboard_products_common
GROUP BY source
ORDER BY total DESC;


-- 1.4. Phân bố nguồn dữ liệu Monitor
SELECT source, COUNT(*) AS total
FROM monitor_products_common
GROUP BY source
ORDER BY total DESC;


-- ============================================================
-- 2. TRUY VẤN SẢN PHẨM THEO GIÁ
-- ============================================================

-- 2.1. Laptop có giá dưới 20 triệu
SELECT
    record_id,
    name,
    brand,
    price_vnd,
    source
FROM laptop_products_common
WHERE price_vnd < 20000000
ORDER BY price_vnd ASC;


-- 2.2. Laptop từ 20 đến 40 triệu
SELECT
    record_id,
    name,
    brand,
    price_vnd,
    source
FROM laptop_products_common
WHERE price_vnd BETWEEN 20000000 AND 40000000
ORDER BY price_vnd ASC;


-- 2.3. Laptop trên 50 triệu
SELECT
    record_id,
    name,
    brand,
    price_vnd,
    source
FROM laptop_products_common
WHERE price_vnd > 50000000
ORDER BY price_vnd DESC;


-- 2.4. Bàn phím dưới 2 triệu
SELECT
    record_id,
    name,
    brand,
    price_vnd,
    source
FROM keyboard_products_common
WHERE price_vnd < 2000000
ORDER BY price_vnd ASC;


-- 2.5. Màn hình dưới 5 triệu
SELECT
    record_id,
    name,
    brand,
    price_vnd,
    source
FROM monitor_products_common
WHERE price_vnd < 5000000
ORDER BY price_vnd ASC;


-- ============================================================
-- 3. TOP SẢN PHẨM THEO GIÁ
-- ============================================================

-- 3.1. 10 laptop đắt nhất
SELECT
    name,
    brand,
    price_vnd,
    source
FROM laptop_products_common
ORDER BY price_vnd DESC
LIMIT 10;


-- 3.2. 10 laptop rẻ nhất
SELECT
    name,
    brand,
    price_vnd,
    source
FROM laptop_products_common
ORDER BY price_vnd ASC
LIMIT 10;


-- 3.3. 10 bàn phím đắt nhất
SELECT
    name,
    brand,
    price_vnd,
    source
FROM keyboard_products_common
ORDER BY price_vnd DESC
LIMIT 10;


-- 3.4. 10 màn hình đắt nhất
SELECT
    name,
    brand,
    price_vnd,
    source
FROM monitor_products_common
ORDER BY price_vnd DESC
LIMIT 10;


-- ============================================================
-- 4. THỐNG KÊ GIÁ
-- ============================================================

-- 4.1. Thống kê giá laptop
SELECT
    COUNT(*) AS total_products,
    MIN(price_vnd) AS min_price,
    MAX(price_vnd) AS max_price,
    ROUND(AVG(price_vnd), 0) AS avg_price
FROM laptop_products_common;


-- 4.2. Thống kê giá keyboard
SELECT
    COUNT(*) AS total_products,
    MIN(price_vnd) AS min_price,
    MAX(price_vnd) AS max_price,
    ROUND(AVG(price_vnd), 0) AS avg_price
FROM keyboard_products_common;


-- 4.3. Thống kê giá monitor
SELECT
    COUNT(*) AS total_products,
    MIN(price_vnd) AS min_price,
    MAX(price_vnd) AS max_price,
    ROUND(AVG(price_vnd), 0) AS avg_price
FROM monitor_products_common;


-- ============================================================
-- 5. THỐNG KÊ THEO THƯƠNG HIỆU
-- ============================================================

-- 5.1. Số laptop theo thương hiệu
SELECT
    brand,
    COUNT(*) AS total_products
FROM laptop_products_common
WHERE brand IS NOT NULL
  AND brand <> ''
GROUP BY brand
ORDER BY total_products DESC;


-- 5.2. Số keyboard theo thương hiệu
SELECT
    brand,
    COUNT(*) AS total_products
FROM keyboard_products_common
WHERE brand IS NOT NULL
  AND brand <> ''
GROUP BY brand
ORDER BY total_products DESC;


-- 5.3. Số monitor theo thương hiệu
SELECT
    brand,
    COUNT(*) AS total_products
FROM monitor_products_common
WHERE brand IS NOT NULL
  AND brand <> ''
GROUP BY brand
ORDER BY total_products DESC;


-- ============================================================
-- 6. SO SÁNH HAI NGUỒN DỮ LIỆU
-- ============================================================

-- 6.1. Giá trung bình laptop theo nguồn
SELECT
    source,
    COUNT(*) AS total_products,
    ROUND(AVG(price_vnd), 0) AS average_price,
    MIN(price_vnd) AS min_price,
    MAX(price_vnd) AS max_price
FROM laptop_products_common
GROUP BY source
ORDER BY average_price DESC;


-- 6.2. Giá trung bình keyboard theo nguồn
SELECT
    source,
    COUNT(*) AS total_products,
    ROUND(AVG(price_vnd), 0) AS average_price,
    MIN(price_vnd) AS min_price,
    MAX(price_vnd) AS max_price
FROM keyboard_products_common
GROUP BY source
ORDER BY average_price DESC;


-- 6.3. Giá trung bình monitor theo nguồn
SELECT
    source,
    COUNT(*) AS total_products,
    ROUND(AVG(price_vnd), 0) AS average_price,
    MIN(price_vnd) AS min_price,
    MAX(price_vnd) AS max_price
FROM monitor_products_common
GROUP BY source
ORDER BY average_price DESC;


-- ============================================================
-- 7. SẢN PHẨM CÓ GIẢM GIÁ
-- ============================================================

-- 7.1. Laptop có giảm giá
SELECT
    name,
    brand,
    price_vnd,
    old_price_vnd,
    discount_amount_vnd,
    discount_percent,
    source
FROM laptop_products_common
WHERE discount_percent IS NOT NULL
  AND discount_percent > 0
ORDER BY discount_percent DESC;


-- 7.2. Keyboard có giảm giá
SELECT
    name,
    brand,
    price_vnd,
    old_price_vnd,
    discount_amount_vnd,
    discount_percent,
    source
FROM keyboard_products_common
WHERE discount_percent IS NOT NULL
  AND discount_percent > 0
ORDER BY discount_percent DESC;


-- 7.3. Monitor có giảm giá
SELECT
    name,
    brand,
    price_vnd,
    old_price_vnd,
    discount_amount_vnd,
    discount_percent,
    source
FROM monitor_products_common
WHERE discount_percent IS NOT NULL
  AND discount_percent > 0
ORDER BY discount_percent DESC;


-- ============================================================
-- 8. JOIN COMMON + SPECS
-- ============================================================

-- 8.1. Laptop + CPU + RAM + SSD
SELECT
    p.name,
    p.brand,
    p.price_vnd,
    p.source,
    s.cpu,
    s.ram_gb,
    s.storage_gb,
    s.gpu
FROM laptop_products_common p
JOIN laptop_specs s
    ON p.record_id = s.record_id
ORDER BY p.price_vnd DESC;


-- 8.2. Laptop có RAM >= 16 GB
SELECT
    p.name,
    p.brand,
    p.price_vnd,
    s.cpu,
    s.ram_gb,
    s.storage_gb,
    p.source
FROM laptop_products_common p
JOIN laptop_specs s
    ON p.record_id = s.record_id
WHERE s.ram_gb >= 16
ORDER BY p.price_vnd ASC;


-- 8.3. Laptop có SSD >= 512 GB
SELECT
    p.name,
    p.brand,
    p.price_vnd,
    s.cpu,
    s.ram_gb,
    s.storage_gb,
    p.source
FROM laptop_products_common p
JOIN laptop_specs s
    ON p.record_id = s.record_id
WHERE s.storage_gb >= 512
ORDER BY p.price_vnd ASC;


-- 8.4. Màn hình >= 144 Hz
SELECT
    p.name,
    p.brand,
    p.price_vnd,
    s.screen_size_inch,
    s.resolution,
    s.refresh_rate_hz,
    s.panel_type,
    p.source
FROM monitor_products_common p
JOIN monitor_specs s
    ON p.record_id = s.record_id
WHERE s.refresh_rate_hz >= 144
ORDER BY s.refresh_rate_hz DESC;


-- 8.5. Màn hình theo kích thước
SELECT
    p.name,
    p.brand,
    p.price_vnd,
    s.screen_size_inch,
    s.resolution,
    s.refresh_rate_hz
FROM monitor_products_common p
JOIN monitor_specs s
    ON p.record_id = s.record_id
WHERE s.screen_size_inch >= 27
ORDER BY s.screen_size_inch DESC;


-- 8.6. Keyboard theo loại kết nối
SELECT
    p.name,
    p.brand,
    p.price_vnd,
    s.connection_type,
    s.keyboard_type,
    s.switch_type,
    s.backlight,
    p.source
FROM keyboard_products_common p
JOIN keyboard_specs s
    ON p.record_id = s.record_id
WHERE s.connection_type IS NOT NULL
ORDER BY p.price_vnd ASC;


-- ============================================================
-- 9. TÌM KIẾM SẢN PHẨM
-- ============================================================

-- 9.1. Tìm laptop chứa từ khóa
SELECT
    name,
    brand,
    price_vnd,
    source
FROM laptop_products_common
WHERE name LIKE '%gaming%'
   OR name LIKE '%Gaming%'
ORDER BY price_vnd ASC;


-- 9.2. Tìm laptop theo thương hiệu
SELECT
    name,
    brand,
    price_vnd,
    source
FROM laptop_products_common
WHERE brand LIKE '%ASUS%'
ORDER BY price_vnd ASC;


-- 9.3. Tìm keyboard cơ
SELECT
    p.name,
    p.brand,
    p.price_vnd,
    s.keyboard_type,
    s.switch_type,
    p.source
FROM keyboard_products_common p
JOIN keyboard_specs s
    ON p.record_id = s.record_id
WHERE s.keyboard_type LIKE '%cơ%'
   OR s.keyboard_type LIKE '%Mechanical%'
ORDER BY p.price_vnd ASC;


-- ============================================================
-- 10. THỐNG KÊ SPECS
-- ============================================================

-- 10.1. RAM phổ biến
SELECT
    s.ram_gb,
    COUNT(*) AS total_products
FROM laptop_specs s
WHERE s.ram_gb IS NOT NULL
GROUP BY s.ram_gb
ORDER BY total_products DESC;


-- 10.2. Dung lượng SSD phổ biến
SELECT
    s.storage_gb,
    COUNT(*) AS total_products
FROM laptop_specs s
WHERE s.storage_gb IS NOT NULL
GROUP BY s.storage_gb
ORDER BY total_products DESC;


-- 10.3. Tần số quét màn hình phổ biến
SELECT
    s.refresh_rate_hz,
    COUNT(*) AS total_products
FROM monitor_specs s
WHERE s.refresh_rate_hz IS NOT NULL
GROUP BY s.refresh_rate_hz
ORDER BY total_products DESC;


-- 10.4. Loại tấm nền màn hình
SELECT
    s.panel_type,
    COUNT(*) AS total_products
FROM monitor_specs s
WHERE s.panel_type IS NOT NULL
GROUP BY s.panel_type
ORDER BY total_products DESC;


-- ============================================================
-- 11. KIỂM TRA CHẤT LƯỢNG DỮ LIỆU
-- ============================================================

-- 11.1. Kiểm tra giá không hợp lệ - Laptop
SELECT COUNT(*) AS invalid_price
FROM laptop_products_common
WHERE price_vnd IS NULL
   OR price_vnd <= 0;


-- 11.2. Kiểm tra giá không hợp lệ - Keyboard
SELECT COUNT(*) AS invalid_price
FROM keyboard_products_common
WHERE price_vnd IS NULL
   OR price_vnd <= 0;


-- 11.3. Kiểm tra giá không hợp lệ - Monitor
SELECT COUNT(*) AS invalid_price
FROM monitor_products_common
WHERE price_vnd IS NULL
   OR price_vnd <= 0;


-- 11.4. Kiểm tra discount không hợp lệ
SELECT COUNT(*) AS invalid_discount
FROM laptop_products_common
WHERE discount_percent IS NOT NULL
  AND (discount_percent < 0 OR discount_percent > 100);


-- 11.5. Kiểm tra record_id trùng
SELECT
    record_id,
    COUNT(*) AS duplicate_count
FROM laptop_products_common
GROUP BY record_id
HAVING COUNT(*) > 1;


-- ============================================================
-- 12. CRUD DEMO
-- ============================================================

-- -------------------------
-- CREATE / INSERT
-- -------------------------

-- Không thực hiện INSERT thật vào dataset chính.
-- Ví dụ:
--
-- INSERT INTO laptop_products_common
-- (
--     record_id,
--     product_id,
--     sku,
--     name,
--     brand,
--     category,
--     price_vnd,
--     source,
--     crawl_date
-- )
-- VALUES
-- (
--     'demo_laptop_001',
--     NULL,
--     NULL,
--     'Demo Laptop',
--     'Demo Brand',
--     'Laptop',
--     10000000,
--     'demo',
--     CURRENT_DATE
-- );


-- -------------------------
-- READ / SELECT
-- -------------------------

SELECT *
FROM laptop_products_common
LIMIT 10;


-- -------------------------
-- UPDATE
-- -------------------------

-- Ví dụ UPDATE an toàn:
-- chỉ cập nhật bản ghi demo nếu tồn tại.

UPDATE laptop_products_common
SET brand = brand
WHERE record_id = 'demo_laptop_001';


-- -------------------------
-- DELETE
-- -------------------------

-- Không xóa dữ liệu thật.
-- Ví dụ:
--
-- DELETE FROM laptop_products_common
-- WHERE record_id = 'demo_laptop_001';


-- ============================================================
-- 13. KIỂM TRA COMMON ↔ SPECS
-- ============================================================

-- Laptop không có specs
SELECT p.record_id
FROM laptop_products_common p
LEFT JOIN laptop_specs s
    ON p.record_id = s.record_id
WHERE s.record_id IS NULL;


-- Specs laptop không có common
SELECT s.record_id
FROM laptop_specs s
LEFT JOIN laptop_products_common p
    ON s.record_id = p.record_id
WHERE p.record_id IS NULL;


-- Keyboard không có specs
SELECT p.record_id
FROM keyboard_products_common p
LEFT JOIN keyboard_specs s
    ON p.record_id = s.record_id
WHERE s.record_id IS NULL;


-- Monitor không có specs
SELECT p.record_id
FROM monitor_products_common p
LEFT JOIN monitor_specs s
    ON p.record_id = s.record_id
WHERE s.record_id IS NULL;


-- ============================================================
-- 14. THỐNG KÊ CUỐI CÙNG CHO BÁO CÁO
-- ============================================================

SELECT
    'Laptop' AS product_type,
    COUNT(*) AS total_products,
    COUNT(DISTINCT source) AS sources,
    ROUND(AVG(price_vnd), 0) AS average_price,
    MIN(price_vnd) AS min_price,
    MAX(price_vnd) AS max_price
FROM laptop_products_common

UNION ALL

SELECT
    'Keyboard',
    COUNT(*),
    COUNT(DISTINCT source),
    ROUND(AVG(price_vnd), 0),
    MIN(price_vnd),
    MAX(price_vnd)
FROM keyboard_products_common

UNION ALL

SELECT
    'Monitor',
    COUNT(*),
    COUNT(DISTINCT source),
    ROUND(AVG(price_vnd), 0),
    MIN(price_vnd),
    MAX(price_vnd)
FROM monitor_products_common;
