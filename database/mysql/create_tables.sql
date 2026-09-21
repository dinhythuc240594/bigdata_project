CREATE DATABASE IF NOT EXISTS bigdata_project
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE bigdata_project;

CREATE TABLE laptops (
    id INT AUTO_INCREMENT PRIMARY KEY,
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

CREATE TABLE hotels (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id BIGINT NOT NULL UNIQUE,
    hotel_code VARCHAR(255) NOT NULL,
    name VARCHAR(500) NOT NULL,
    star_rating DECIMAL(2,1),
    review_score DECIMAL(3,1),
    review_count INT,
    min_price_vnd BIGINT NOT NULL,
    max_price_vnd BIGINT NOT NULL,
    deal_price_vnd BIGINT,
    address VARCHAR(500),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    description TEXT,
    facilities TEXT,
    location_tags TEXT,
    hotel_url VARCHAR(1000) NOT NULL,
    source VARCHAR(100) NOT NULL,
    crawl_date DATE NOT NULL,
    check_in DATE,
    check_out DATE
);
