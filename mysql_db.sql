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


-- Create the social_data table
CREATE TABLE IF NOT EXISTS social (
    CompanyID INT NOT NULL,
    ReportYear INT NOT NULL,
    EmployeeCount INT,
    MalePercentage DECIMAL(5,2),
    FemalePercentage DECIMAL(5,2),
    AgeUnder30 DECIMAL(5,2),
    Age30to50 DECIMAL(5,2),
    AgeAbove50 DECIMAL(5,2),
    TrainingHours DECIMAL(10,1),
    CommunityInvestmentUSD DECIMAL(12,0),
    PRIMARY KEY (CompanyID, ReportYear),
    FOREIGN KEY (CompanyID) REFERENCES company_info(CompanyID)
);

-- Insert data into the social_data table
INSERT INTO social (CompanyID, ReportYear, EmployeeCount, MalePercentage, FemalePercentage, AgeUnder30, Age30to50, AgeAbove50, TrainingHours, CommunityInvestmentUSD)
VALUES
(7, 2023, 204000, 65.90, 34.10, 40, 35, 15, NULL, NULL),
(7, 2022, 190234, 65.90, 34.10, 40, 35, 15, NULL, NULL),
(7, 2021, 186779, 66.10, 33.90, 40, 35, 15, NULL, NULL),
(7, 2020, 156500, 67.50, 32.50, 40, 35, 15, NULL, NULL),
(7, 2019, 118899, 68.00, 32.00, 40, 35, 15, NULL, NULL),
(6, 2022, 270372, 64.9, 35.1, 31, NULL, NULL, 914000, NULL),
(6, 2021, 266673, 63.7, 36.3, 33.72, NULL, NULL, 818000, NULL),
(6, 2020, 267937, 62.7, 37.3, 38, NULL, NULL, 734000, NULL),
(3, 2023, 35116, 73.65, 26.35, 35.76, 63.51, 0.73, 172705, NULL),
(3, 2022, 35997, 69.35, 30.65, 39.4, 59.74, 0.86, 302383, NULL),
(3, 2021, 33415, 66.7, 33.3, 43.69, 55.51, 0.8, 363531, NULL),
(3, 2020, 24810, NULL, NULL, 47.32, 52.14, 0.53, NULL, NULL),
(5, 2023, 67317, 63.30, 36.70, NULL, NULL, NULL, NULL, NULL),
(5, 2022, 86482, 62.90, 37.10, NULL, NULL, NULL, NULL, NULL),
(5, 2021, 71970, 63.30, 36.70, NULL, NULL, NULL, NULL, NULL),
(5, 2020, 58604, 63.00, 37.00, NULL, NULL, NULL, NULL, NULL),
(1, 2023, 161000, 64.41, 35.59, NULL, NULL, NULL, NULL, NULL),
(1, 2022, 164000, 64.60, 35.30, NULL, NULL, NULL, NULL, NULL),
(1, 2021, 154000, 65.20, 34.80, NULL, NULL, NULL, NULL, NULL),
(1, 2020, 147000, 66.00, 34.00, NULL, NULL, NULL, NULL, NULL),
(1, 2019, 137000, 67.00, 33.00, NULL, NULL, NULL, NULL, NULL),
(4, 2023, 282200, 62.60, 37.40, NULL, NULL, NULL, 23100000, NULL),
(4, 2022, 288300, 62.80, 37.20, NULL, NULL, NULL, 24300000, NULL),
(4, 2021, 282100, 63.30, 36.70, NULL, NULL, NULL, 22500000, NULL),
(4, 2020, 345900, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(4, 2019, 352600, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(2, 2023, 69500, 63.00, 37.00, 14, 72, 14, 625500, 17897690),
(2, 2022, 77000, 63.00, 37.00, 15, 72, 13, 462000, 28340914),
(2, 2021, 75000, 63.00, 37.00, 15, 73, 12, 375000, 20867596),
(2, 2020, 71500, 64.00, 36.00, 15, 73, 12, NULL, 11831274),
(2, 2019, 63000, 64.00, 36.00, NULL, NULL, NULL, NULL, 14482776),
(8, 2023, 56780, 71.27, 28.73, 31.38, 68.02, 0.60, 1465109.1, NULL),
(8, 2022, 61328, 71.24, 28.76, 36.97, 62.61, 0.42, 2225679.7, NULL),
(8, 2021, 68226, 70.95, 29.05, 41.93, 57.78, 0.29, 2795780.2, NULL);


    -- Drop the existing e_score table if it exists
    DROP TABLE IF EXISTS e_score;

    -- Create the e_score table with all columns including update_time
    CREATE TABLE e_score (
        CompanyID INT NOT NULL,
        ReportYear INT NOT NULL,
        Energy_score DECIMAL(5,2),
        Water_score DECIMAL(5,2),
        GHG_score DECIMAL(5,2),
        Waste_score DECIMAL(5,2),
        Renewable_score DECIMAL(5,2),
        Energy_score_weighted DECIMAL(5,2),
        Water_score_weighted DECIMAL(5,2),
        GHG_score_weighted DECIMAL(5,2),
        Waste_score_weighted DECIMAL(5,2),
        Renewable_score_weighted DECIMAL(5,2),
        env_score_weighted DECIMAL(5,2),
        update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        PRIMARY KEY (CompanyID, ReportYear),
        FOREIGN KEY (CompanyID) REFERENCES company_info(CompanyID)
    );

