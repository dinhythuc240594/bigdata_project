-- ============================================================
-- BIG DATA PROJECT - MySQL QUERIES
-- Database: bigdata_project
-- ============================================================

USE bigdata_project;

-- 1. Record counts
SELECT 'laptops' AS table_name, COUNT(*) AS total_records FROM laptops
UNION ALL
SELECT 'hotels', COUNT(*) FROM hotels;

-- 2. Sample data
SELECT * FROM laptops LIMIT 10;
SELECT * FROM hotels LIMIT 10;

-- 3. Laptops by brand
SELECT brand, COUNT(*) AS total_laptops
FROM laptops
GROUP BY brand
ORDER BY total_laptops DESC;

-- 4. Average laptop price by brand
SELECT brand, COUNT(*) AS total_laptops,
       ROUND(AVG(price_vnd), 0) AS average_price_vnd,
       MIN(price_vnd) AS min_price_vnd,
       MAX(price_vnd) AS max_price_vnd
FROM laptops
GROUP BY brand
ORDER BY average_price_vnd DESC;

-- 5. Top 10 most expensive laptops
SELECT name, brand, price_vnd, ram_gb, storage_gb, cpu, gpu
FROM laptops
ORDER BY price_vnd DESC
LIMIT 10;

-- 6. Top 10 cheapest laptops
SELECT name, brand, price_vnd, ram_gb, storage_gb
FROM laptops
ORDER BY price_vnd ASC
LIMIT 10;

-- 7. Laptops with RAM >= 32 GB
SELECT name, brand, price_vnd, ram_gb, storage_gb
FROM laptops
WHERE ram_gb >= 32
ORDER BY ram_gb DESC, price_vnd DESC;

-- 8. Laptops with storage >= 1 TB
SELECT name, brand, price_vnd, ram_gb, storage_gb
FROM laptops
WHERE storage_gb >= 1024
ORDER BY storage_gb DESC, price_vnd ASC;

-- 9. Laptops with rating >= 4.5
SELECT name, brand, price_vnd, rating, review_count
FROM laptops
WHERE rating >= 4.5
ORDER BY rating DESC, review_count DESC;

-- 10. Laptop price statistics
SELECT COUNT(*) AS total,
       MIN(price_vnd) AS min_price,
       ROUND(AVG(price_vnd), 0) AS avg_price,
       MAX(price_vnd) AS max_price
FROM laptops;

-- 11. Laptops by RAM
SELECT ram_gb, COUNT(*) AS total_laptops
FROM laptops
GROUP BY ram_gb
ORDER BY ram_gb;

-- 12. Laptops by storage
SELECT storage_gb, COUNT(*) AS total_laptops
FROM laptops
GROUP BY storage_gb
ORDER BY storage_gb;

-- 13. Hotels by star rating
SELECT star_rating, COUNT(*) AS total_hotels
FROM hotels
GROUP BY star_rating
ORDER BY star_rating DESC;

-- 14. Hotel price statistics by star rating
SELECT star_rating, COUNT(*) AS total_hotels,
       ROUND(AVG(min_price_vnd), 0) AS average_min_price_vnd,
       MIN(min_price_vnd) AS min_price_vnd,
       MAX(max_price_vnd) AS max_price_vnd
FROM hotels
GROUP BY star_rating
ORDER BY star_rating DESC;

-- 15. Top 10 hotels by review score
SELECT name, star_rating, review_score, review_count,
       min_price_vnd, max_price_vnd
FROM hotels
ORDER BY review_score DESC, review_count DESC
LIMIT 10;

-- 16. Top 10 cheapest hotels
SELECT name, star_rating, review_score,
       min_price_vnd, max_price_vnd
FROM hotels
ORDER BY min_price_vnd ASC
LIMIT 10;

-- 17. Top 10 most expensive hotels
SELECT name, star_rating, review_score,
       min_price_vnd, max_price_vnd
FROM hotels
ORDER BY min_price_vnd DESC
LIMIT 10;

-- 18. Hotels with review score >= 9
SELECT name, star_rating, review_score, review_count, min_price_vnd
FROM hotels
WHERE review_score >= 9
ORDER BY review_score DESC, review_count DESC;

-- 19. Hotels with a valid deal lower than the minimum listed price
SELECT name, star_rating, min_price_vnd, deal_price_vnd,
       (min_price_vnd - deal_price_vnd) AS saving_vnd
FROM hotels
WHERE deal_price_vnd IS NOT NULL
  AND deal_price_vnd > 0
  AND deal_price_vnd < min_price_vnd
ORDER BY saving_vnd DESC;

-- 20. Data quality: important laptop fields
SELECT
    SUM(name IS NULL OR name = '') AS missing_name,
    SUM(brand IS NULL OR brand = '') AS missing_brand,
    SUM(price_vnd IS NULL) AS missing_price,
    SUM(url IS NULL OR url = '') AS missing_url
FROM laptops;

-- 21. Data quality: important hotel fields
SELECT
    SUM(hotel_id IS NULL) AS missing_hotel_id,
    SUM(name IS NULL OR name = '') AS missing_name,
    SUM(min_price_vnd IS NULL) AS missing_min_price,
    SUM(max_price_vnd IS NULL) AS missing_max_price,
    SUM(hotel_url IS NULL OR hotel_url = '') AS missing_url
FROM hotels;

-- 22. Duplicate laptop URLs
SELECT url, COUNT(*) AS duplicate_count
FROM laptops
GROUP BY url
HAVING COUNT(*) > 1;

-- 23. Duplicate hotel IDs
SELECT hotel_id, COUNT(*) AS duplicate_count
FROM hotels
GROUP BY hotel_id
HAVING COUNT(*) > 1;

-- 24. CRUD - READ example
SELECT * FROM laptops
WHERE brand = 'ASUS'
LIMIT 10;

-- CRUD INSERT/UPDATE/DELETE examples are intentionally commented out.
-- INSERT INTO laptops (...) VALUES (...);
-- UPDATE laptops SET price_vnd = price_vnd - 100000 WHERE id = 1;
-- DELETE FROM laptops WHERE id = 1;

-- 25. Project-level source summary
SELECT 'The Gioi Di Dong' AS data_source, COUNT(*) AS total_records
FROM laptops
UNION ALL
SELECT 'iVIVU', COUNT(*) FROM hotels;
