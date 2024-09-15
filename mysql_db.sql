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


-- Create the environment table
CREATE TABLE environment (
    CompanyID INT NOT NULL,
    ReportYear INT NOT NULL,
    EnergyConsumption DECIMAL(15,2),
    GHGEmissions DECIMAL(15,2),
    WaterUsage DECIMAL(15,2),
    WasteGenerated DECIMAL(15,2),
    RenewableEnergyUse DECIMAL(15,2),
    PRIMARY KEY (CompanyID, ReportYear),
    FOREIGN KEY (CompanyID) REFERENCES company_info(CompanyID)
);

-- Insert data into the environment table
INSERT INTO environment (CompanyID, ReportYear, EnergyConsumption, GHGEmissions, WaterUsage, WasteGenerated, RenewableEnergyUse)
VALUES
(3, 2023, 211171.84, 116722.56, 1371360.69, 7270.61, NULL),
(3, 2022, 144741.38, 85742.61, 1020312.10, 7053.71, NULL),
(3, 2021, 144626.56, 82820.16, 927326.00, 6331.38, NULL),
(3, 2020, 118397.58, 66481.29, 606265.84, 4661.44, NULL),
(4, 2019, 2837000, 809000, NULL, 31500, NULL),
(4, 2020, 2529000, 569000, NULL, 22100, NULL),
(4, 2021, 2846000, 475000, NULL, 20700, NULL),
(4, 2022, 2448000, 430000, NULL, 14800, NULL),
(4, 2023, 2287000, 364000, NULL, 16500, NULL),
(6, 2022, 35177000, 15053000, 172811000, 1413365, 8704000),
(6, 2021, 32322000, 17400000, 163660000, 1324972, 5278000),
(6, 2020, 29024000, 14806000, 141648000, 1181741, 4030000),
(5, 2023, 15543490, 7443182, 5274000, 38468, 15543490),
(5, 2022, 11822293, 8453471, 4893023, 18519, 11822293),
(5, 2021, 9689497, 5740244, 5042564, 18430, 9689497),
(5, 2020, 7520839, 4984000, 3726000, 10000, 7520839),
(1, 2023, 483299062, 324100, 6100000, 497000, 3489000),
(1, 2022, 487921930, 324000, 5800000, 523000, 3199000),
(1, 2021, 384727076, 166380, 5300000, 419000, 2854000),
(1, 2020, 372901398, 334430, 4900000, 400000, 2580000),
(1, 2019, 339047649, 573730, 4900000, 322000, 2430000),
(2, 2023, 377338, 219825, 1420000, 48452, 16956),
(2, 2022, 392825, 228282, 1499000, 51099, 13333),
(2, 2021, 366885, 210007, 1567000, 49528, 9360),
(2, 2020, 346683, 206466, 1428000, 51685, 9065),
(2, 2019, 327798, 194215, 1307000, NULL, 4226),
(7, 2023, 25910500, 14314800, 6352.00, 41100, 25307000),
(7, 2022, 22367100, 12617400, 5564.70, 38200, 21776200),
(7, 2021, 18639900, 10775200, 4561.80, 28200, 18287100),
(7, 2020, 15492000, 8567200, 3748.90, 28900, 15138500),
(7, 2019, 12801900, 9671400, 3412.40, 48100, 12237200),
(8, 2023, 5165168.20, 5793823.70, 8191328.40, 47858.1, 604277.10),
(8, 2022, 5046045.10, 5739723.70, 8152481.90, 34113.4, 336419.50),
(8, 2021, 4452650.10, 5871780.70, 6201651.60, 30173.6, 63000.00);
