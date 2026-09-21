-- ============================================================
-- BIG DATA PROJECT - MySQL DATABASE SCHEMA v2
-- Updated: TGDD product_id included
-- ============================================================

CREATE DATABASE IF NOT EXISTS bigdata_project
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE bigdata_project;

DROP TABLE IF EXISTS laptops;
DROP TABLE IF EXISTS hotels;

-- ============================================================
-- 1. THẾ GIỚI DI ĐỘNG - LAPTOPS
-- ============================================================

CREATE TABLE laptops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id BIGINT NOT NULL UNIQUE,
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    price_vnd BIGINT NOT NULL,
    old_price_vnd BIGINT NULL,
    discount_percent DECIMAL(5,2) NULL,
    rating DECIMAL(3,1) NULL,
    review_count INT NULL,
    screen_size_inch DECIMAL(4,1) NULL,
    cpu VARCHAR(255) NULL,
    gpu VARCHAR(255) NULL,
    ram_gb INT NULL,
    storage_gb INT NULL,
    weight_kg DECIMAL(5,2) NULL,
    url VARCHAR(1000) NOT NULL,
    source VARCHAR(100) NOT NULL,
    crawl_date DATE NOT NULL
);

-- ============================================================
-- 2. IVIVU - HOTELS
-- ============================================================

CREATE TABLE hotels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id BIGINT NOT NULL UNIQUE,
    hotel_code VARCHAR(255) NOT NULL,
    name VARCHAR(500) NOT NULL,
    star_rating DECIMAL(2,1) NULL,
    review_score DECIMAL(3,1) NULL,
    review_count INT NULL,
    min_price_vnd BIGINT NOT NULL,
    max_price_vnd BIGINT NOT NULL,
    deal_price_vnd BIGINT NULL,
    address VARCHAR(500) NULL,
    latitude DECIMAL(10,7) NULL,
    longitude DECIMAL(10,7) NULL,
    description TEXT NULL,
    facilities TEXT NULL,
    location_tags TEXT NULL,
    hotel_url VARCHAR(1000) NOT NULL,
    source VARCHAR(100) NOT NULL,
    crawl_date DATE NOT NULL,
    check_in DATE NULL,
    check_out DATE NULL
);

-- ============================================================
-- 3. BASIC INDEXES
-- ============================================================

CREATE INDEX idx_laptops_brand ON laptops(brand);
CREATE INDEX idx_laptops_price ON laptops(price_vnd);
CREATE INDEX idx_laptops_ram ON laptops(ram_gb);
CREATE INDEX idx_laptops_storage ON laptops(storage_gb);

CREATE INDEX idx_hotels_star ON hotels(star_rating);
CREATE INDEX idx_hotels_min_price ON hotels(min_price_vnd);
CREATE INDEX idx_hotels_review_score ON hotels(review_score);
