-- ============================================================
-- BIG DATA PROJECT
-- MySQL Database Schema
-- Sources:
--   1. Thế Giới Di Động
--   2. Phong Vũ
--
-- Categories:
--   1. Laptop
--   2. Keyboard
--   3. Monitor
-- ============================================================

CREATE DATABASE IF NOT EXISTS bigdata_project
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE bigdata_project;


-- ============================================================
-- 1. LAPTOP - COMMON
-- ============================================================

CREATE TABLE IF NOT EXISTS laptop_products_common (
    record_id VARCHAR(255) NOT NULL,
    product_id BIGINT NULL,
    sku VARCHAR(255) NULL,
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(255) NULL,
    category VARCHAR(100) NULL,

    price_vnd BIGINT NULL,
    old_price_vnd BIGINT NULL,
    discount_amount_vnd BIGINT NULL,
    discount_percent DECIMAL(6,2) NULL,

    rating DECIMAL(3,1) NULL,
    review_count INT NULL,

    url VARCHAR(1000) NULL,
    source VARCHAR(100) NOT NULL,
    crawl_date DATE NULL,

    PRIMARY KEY (record_id),

    INDEX idx_laptop_product_id (product_id),
    INDEX idx_laptop_sku (sku),
    INDEX idx_laptop_brand (brand),
    INDEX idx_laptop_price (price_vnd),
    INDEX idx_laptop_source (source),
    INDEX idx_laptop_category (category)
);


-- ============================================================
-- 2. LAPTOP - SPECS
-- ============================================================

CREATE TABLE IF NOT EXISTS laptop_specs (
    record_id VARCHAR(255) NOT NULL,
    product_id BIGINT NULL,
    sku VARCHAR(255) NULL,

    cpu VARCHAR(500) NULL,
    ram_gb DECIMAL(10,2) NULL,
    storage_gb DECIMAL(10,2) NULL,
    gpu VARCHAR(500) NULL,
    screen_size_inch DECIMAL(10,2) NULL,
    weight_kg DECIMAL(10,2) NULL,

    PRIMARY KEY (record_id),

    INDEX idx_laptop_specs_product_id (product_id),
    INDEX idx_laptop_specs_sku (sku),
    INDEX idx_laptop_specs_cpu (cpu),
    INDEX idx_laptop_specs_ram (ram_gb),
    INDEX idx_laptop_specs_storage (storage_gb)
);


-- ============================================================
-- 3. KEYBOARD - COMMON
-- ============================================================

CREATE TABLE IF NOT EXISTS keyboard_products_common (
    record_id VARCHAR(255) NOT NULL,
    product_id BIGINT NULL,
    sku VARCHAR(255) NULL,
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(255) NULL,
    category VARCHAR(100) NULL,

    price_vnd BIGINT NULL,
    old_price_vnd BIGINT NULL,
    discount_amount_vnd BIGINT NULL,
    discount_percent DECIMAL(6,2) NULL,

    rating DECIMAL(3,1) NULL,
    review_count INT NULL,

    url VARCHAR(1000) NULL,
    source VARCHAR(100) NOT NULL,
    crawl_date DATE NULL,

    PRIMARY KEY (record_id),

    INDEX idx_keyboard_product_id (product_id),
    INDEX idx_keyboard_sku (sku),
    INDEX idx_keyboard_brand (brand),
    INDEX idx_keyboard_price (price_vnd),
    INDEX idx_keyboard_source (source),
    INDEX idx_keyboard_category (category)
);


-- ============================================================
-- 4. KEYBOARD - SPECS
-- ============================================================

CREATE TABLE IF NOT EXISTS keyboard_specs (
    record_id VARCHAR(255) NOT NULL,
    product_id BIGINT NULL,
    sku VARCHAR(255) NULL,

    connection_type VARCHAR(255) NULL,
    keyboard_type VARCHAR(255) NULL,
    switch_type VARCHAR(255) NULL,
    layout VARCHAR(255) NULL,
    backlight VARCHAR(255) NULL,

    PRIMARY KEY (record_id),

    INDEX idx_keyboard_specs_product_id (product_id),
    INDEX idx_keyboard_specs_sku (sku),
    INDEX idx_keyboard_specs_connection (connection_type),
    INDEX idx_keyboard_specs_switch (switch_type)
);


-- ============================================================
-- 5. MONITOR - COMMON
-- ============================================================

CREATE TABLE IF NOT EXISTS monitor_products_common (
    record_id VARCHAR(255) NOT NULL,
    product_id BIGINT NULL,
    sku VARCHAR(255) NULL,
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(255) NULL,
    category VARCHAR(100) NULL,

    price_vnd BIGINT NULL,
    old_price_vnd BIGINT NULL,
    discount_amount_vnd BIGINT NULL,
    discount_percent DECIMAL(6,2) NULL,

    rating DECIMAL(3,1) NULL,
    review_count INT NULL,

    url VARCHAR(1000) NULL,
    source VARCHAR(100) NOT NULL,
    crawl_date DATE NULL,

    PRIMARY KEY (record_id),

    INDEX idx_monitor_product_id (product_id),
    INDEX idx_monitor_sku (sku),
    INDEX idx_monitor_brand (brand),
    INDEX idx_monitor_price (price_vnd),
    INDEX idx_monitor_source (source),
    INDEX idx_monitor_category (category)
);


-- ============================================================
-- 6. MONITOR - SPECS
-- ============================================================

CREATE TABLE IF NOT EXISTS monitor_specs (
    record_id VARCHAR(255) NOT NULL,
    product_id BIGINT NULL,
    sku VARCHAR(255) NULL,

    screen_size_inch DECIMAL(10,2) NULL,
    resolution VARCHAR(255) NULL,
    refresh_rate_hz DECIMAL(10,2) NULL,
    panel_type VARCHAR(255) NULL,
    response_time_ms DECIMAL(10,2) NULL,

    PRIMARY KEY (record_id),

    INDEX idx_monitor_specs_product_id (product_id),
    INDEX idx_monitor_specs_sku (sku),
    INDEX idx_monitor_specs_screen_size (screen_size_inch),
    INDEX idx_monitor_specs_refresh_rate (refresh_rate_hz),
    INDEX idx_monitor_specs_panel (panel_type)
);


-- ============================================================
-- END
-- ============================================================

SHOW TABLES;
