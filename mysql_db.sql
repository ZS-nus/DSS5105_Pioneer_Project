-- Create DESIGNLogin database
CREATE DATABASE pioneerDB;

-- Select the DESIGNLogin database
USE pioneerDB;

-- Create Users table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);


-- Insert a row into Users table
INSERT INTO Users (username, password) VALUES ('admin', '123456');

-- Create company_info table
CREATE TABLE company_info (
    CompanyID INT PRIMARY KEY AUTO_INCREMENT,
    CompanyName VARCHAR(255) NOT NULL,
    Sector VARCHAR(255) NOT NULL,
    Location VARCHAR(255) NOT NULL,
    FoundedYear INT,
    Website VARCHAR(255)
);

-- Insert data into company_info table
INSERT INTO company_info (CompanyID, CompanyName, Sector, Location, FoundedYear, Website) VALUES
(1, 'Apple', 'Technology', 'US', 1976, 'https://www.apple.com'),
(2, 'Lenovo', 'Technology', 'China', 1984, 'https://www.lenovo.com'),
(3, 'XiaoMi', 'Technology', 'China', 2010, 'https://www.mi.com'),
(4, 'IBM', 'Technology', 'US', 1911, 'https://www.ibm.com'),
(5, 'Meta', 'Technology', 'US', 2004, 'https://www.meta.com'),
(6, 'Samsung', 'Technology', 'South Korea', 1938, 'https://www.samsung.com'),
(7, 'Google', 'Technology', 'US', 1998, 'https://www.google.com'),
(8, 'Tencent', 'Technology', 'China', 1998, 'https://www.tencent.com');



