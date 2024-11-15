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
    PRIMARY KEY (CompanyID, ReportYear),
    FOREIGN KEY (CompanyID) REFERENCES company_info(CompanyID)
);

-- Insert data into the environment table
INSERT INTO environment (CompanyID, ReportYear, EnergyConsumption, GHGEmissions, WaterUsage, WasteGenerated)
VALUES
(3, 2023, 211171.84, 116722.56, 1371360.69, 7270.61),
(3, 2022, 144741.38, 85742.61, 1020312.10, 7053.71),
(3, 2021, 144626.56, 82820.16, 927326.00, 6331.38),
(3, 2020, 118397.58, 66481.29, 606265.84, 4661.44),
(4, 2019, 2837000, 809000, NULL, 31500),
(4, 2020, 2529000, 569000, NULL, 22100),
(4, 2021, 2846000, 475000, NULL, 20700),
(4, 2022, 2448000, 430000, NULL, 14800),
(4, 2023, 2287000, 364000, NULL, 16500),
(6, 2023, 36399000, 13291000, 177361000, 1314923),
(6, 2022, 35177000, 15053000, 172811000, 1413365),
(6, 2021, 32322000, 17400000, 163660000, 1324972),
(6, 2020, 29024000, 14806000, 141648000, 1181741),
(5, 2023, 15543490, 7443182, 5274000, 38468),
(5, 2022, 11822293, 8453471, 4893023, 18519),
(5, 2021, 9689497, 5740244, 5042564, 18430),
(5, 2020, 7520839, 4984000, 3726000, 10000),
(1, 2023, 483299062, 324100, 6100000, 497000),
(1, 2022, 487921930, 324000, 5800000, 523000),
(1, 2021, 384727076, 166380, 5300000, 419000),
(1, 2020, 372901398, 334430, 4900000, 400000),
(1, 2019, 339047649, 573730, 4900000, 322000),
(2, 2023, 377338, 219825, 1420000, 48452),
(2, 2022, 392825, 228282, 1499000, 51099),
(2, 2021, 366885, 210007, 1567000, 49528),
(2, 2020, 346683, 206466, 1428000, 51685),
(2, 2019, 327798, 194215, 1307000, NULL),
(7, 2023, 25910500, 14314800, 6352.00, 41100),
(7, 2022, 22367100, 12617400, 5564.70, 38200),
(7, 2021, 18639900, 10775200, 4561.80, 28200),
(7, 2020, 15492000, 8567200, 3748.90, 28900),
(7, 2019, 12801900, 9671400, 3412.40, 48100),
(8, 2023, 5165168.20, 5793823.70, 8191328.40, 47858.1),
(8, 2022, 5046045.10, 5739723.70, 8152481.90, 34113.4),
(8, 2021, 4452650.10, 5871780.70, 6201651.60, 30173.6);


-- Create the env_score table
CREATE TABLE env_score (
    CompanyID INT NOT NULL,
    ReportYear INT NOT NULL,
    Energy_score DECIMAL(5,2),
    GHG_score DECIMAL(5,2),
    Water_score DECIMAL(5,2),
    Waste_score DECIMAL(5,2),
    PRIMARY KEY (CompanyID, ReportYear),
    FOREIGN KEY (CompanyID) REFERENCES company_info(CompanyID)
);


-- Drop the existing social table
DROP TABLE IF EXISTS social;

-- Create the modified social table
CREATE TABLE social (
    CompanyID INT NOT NULL,
    ReportYear INT NOT NULL,
    EmployeeCount INT,
    DataSecurity BOOLEAN,
    CustomerPrivacy BOOLEAN,
    Cybersecurity BOOLEAN,
    MalePercentage DECIMAL(5,2),
    FemalePercentage DECIMAL(5,2),
    TrainingHours DECIMAL(10,1),
    WorkRelatedInjuries VARCHAR(255),
    GenderStats BOOLEAN,
    AgeStats BOOLEAN,
    PRIMARY KEY (CompanyID, ReportYear),
    FOREIGN KEY (CompanyID) REFERENCES company_info(CompanyID)
);

-- Insert data into the social table
INSERT INTO social (CompanyID, ReportYear, EmployeeCount, DataSecurity, CustomerPrivacy, Cybersecurity, MalePercentage, FemalePercentage, TrainingHours, WorkRelatedInjuries, GenderStats, AgeStats)
VALUES
(7, 2023, 204000, 0, 0, 0, 65.90, 34.10, NULL, NULL, 1, 1),
(7, 2022, 190234, 0, 0, 0, 65.90, 34.10, NULL, NULL, 1, 1),
(7, 2021, 186779, 0, 0, 0, 66.10, 33.90, NULL, NULL, 1, 1),
(7, 2020, 156500, 0, 0, 0, 67.50, 32.50, NULL, NULL, 1, 1),
(7, 2019, 118899, 0, 0, 0, 68.00, 32.00, NULL, NULL, 1, 1),
(6, 2023, 267860, 1, 1, 1, 71.60, 28.40, 9500000.0, '0.025', 1, 1),
(6, 2022, 270372, 1, 1, 1, 64.90, 35.10, 9140000.0, '0.031', 1, 1),
(6, 2021, 266673, 1, 1, 1, 63.70, 36.30, 8180000.0, '0.022', 1, 1),
(6, 2020, 267937, 1, 1, 1, 62.70, 37.30, 7340000.0, '0.008', 1, 1),
(3, 2023, 35116, 1, 1, 1, 73.65, 26.35, 172705.0, NULL, 1, 1),
(3, 2022, 35997, 1, 1, 1, 69.35, 30.65, 302383.0, NULL, 1, 1),
(3, 2021, 33415, 1, 1, 1, 66.70, 33.30, 363531.0, NULL, 1, 1),
(3, 2020, 24810, 1, 1, 1, NULL, NULL, NULL, '0.000045', 0, 1),
(5, 2023, 67317, 0, 0, 0, 63.30, 36.70, NULL, NULL, 1, 0),
(5, 2022, 86482, 0, 0, 0, 62.90, 37.10, NULL, NULL, 1, 0),
(5, 2021, 71970, 0, 0, 0, 63.30, 36.70, NULL, NULL, 1, 0),
(5, 2020, 58604, 0, 0, 0, 63.00, 37.00, NULL, NULL, 1, 0),
(1, 2023, 161000, 1, 1, 1, 64.41, 35.59, NULL, NULL, 1, 0),
(1, 2022, 164000, 1, 1, 1, 64.60, 35.30, NULL, NULL, 1, 0),
(1, 2021, 154000, 1, 1, 1, 65.20, 34.80, NULL, NULL, 1, 0),
(1, 2020, 147000, 1, 1, 1, 66.00, 34.00, NULL, NULL, 1, 0),
(1, 2019, 137000, 1, 1, 1, 67.00, 33.00, NULL, NULL, 1, 0),
(4, 2023, 282200, 1, 0, 1, 62.60, 37.40, 23100000.0, '0.049', 1, 0),
(4, 2022, 288300, 1, 0, 1, 62.80, 37.20, 24300000.0, NULL, 1, 0),
(4, 2021, 282100, 1, 0, 1, 63.30, 36.70, 22500000.0, NULL, 1, 0),
(4, 2020, 345900, 0, 0, 0, NULL, NULL, NULL, NULL, 0, 0),
(4, 2019, 352600, 0, 0, 0, NULL, NULL, NULL, NULL, 0, 0),
(2, 2023, 69500, 1, 1, 1, 63.00, 37.00, 625500.0, NULL, 1, 1),
(2, 2022, 77000, 1, 1, 1, 63.00, 37.00, 462000.0, '0.002', 1, 1),
(2, 2021, 75000, 0, 1, 1, 63.00, 37.00, 375000.0, NULL, 1, 1),
(2, 2020, 71500, 0, 1, 1, 64.00, 36.00, NULL, NULL, 1, 1),
(2, 2019, 63000, 0, 1, 1, 64.00, 36.00, NULL, NULL, 1, 0),
(8, 2023, 56780, 1, 1, 1, 71.27, 28.73, 1465109.1, '0.13', 1, 1),
(8, 2022, 61328, 1, 1, 1, 71.24, 28.76, 2225679.7, '0.09', 1, 1),
(8, 2021, 68226, 1, 1, 1, 70.95, 29.05, 2795780.2, '0.25', 1, 1);


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

-- Drop the existing governance table if it exists
DROP TABLE IF EXISTS governance;

-- Create the governance_data table
CREATE TABLE IF NOT EXISTS governance (
    CompanyID INT NOT NULL,
    ReportYear INT NOT NULL,
    BoardComposition BOOLEAN,
    EthicalBehaviour BOOLEAN,
    RiskManagement BOOLEAN,
    CertificationList INT,
    PRIMARY KEY (CompanyID, ReportYear),
    FOREIGN KEY (CompanyID) REFERENCES company_info(CompanyID)
);

-- Insert data into the governance table
INSERT INTO governance (CompanyID, ReportYear, BoardComposition, EthicalBehaviour, RiskManagement, CertificationList)
VALUES
(7, 2023, 0, 1, 1, 2),
(7, 2022, 0, 1, 1, 2),
(7, 2021, 0, 1, 1, 2),
(7, 2020, 0, 1, 1, 2),
(7, 2019, 0, 1, 1, 2),
(6, 2023, 1, 1, 1, 5),
(6, 2022, 1, 1, 1, 5),
(6, 2021, 1, 1, 1, 5),
(6, 2020, 1, 1, 1, 5),
(1, 2023, 1, 1, 1, 2),
(1, 2022, 1, 1, 1, 2),
(1, 2021, 1, 1, 1, 2),
(1, 2020, 1, 1, 1, 2),
(1, 2019, 1, 1, 1, 2),
(2, 2023, 0, 0, 1, 3),
(2, 2022, 0, 0, 1, 3),
(2, 2021, 0, 0, 1, 3),
(2, 2020, 0, 0, 1, 3),
(2, 2019, 0, 0, 1, 3),
(3, 2023, 1, 1, 1, 3),
(3, 2022, 1, 1, 1, 3),
(3, 2021, 1, 1, 1, 3),
(3, 2020, 1, 1, 1, 3),
(5, 2023, 0, 1, 1, 1),
(5, 2022, 0, 1, 1, 1),
(5, 2021, 0, 1, 1, 1),
(5, 2020, 0, 1, 1, 1),
(4, 2023, 1, 1, 1, 0),
(4, 2022, 0, 0, 1, 4),
(4, 2021, 0, 0, 1, 4),
(4, 2020, 1, 1, 1, 4),
(4, 2019, 0, 0, 1, 4),
(8, 2023, 1, 1, 1, 4),
(8, 2022, 1, 1, 1, 4),
(8, 2021, 1, 1, 1, 4);

CREATE TABLE IF NOT EXISTS users (
    uid VARCHAR(128) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sign_in_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert the three users
INSERT INTO users (uid, email, user_name, user_role) VALUES
('jbG4LvsLlahschSvyHqWCiaH7OB3', 'e1351499@hotmail.com', 'MING YUE', 'admin'),
('9dura5GhsjYZTrOjTrKKNtDoQk73', 'zs@pioneer.com', 'ZHAOSHENG', 'admin'),
('iI2Oa6xbt9aoWswUFkLUmfz8uB13', 'admin@pioneer.com', 'ZHAOSHENG', 'admin');

-- Drop the existing esg_scores table if it exists
DROP TABLE IF EXISTS esg_scores;

-- Create the esg_scores table
CREATE TABLE esg_scores (
    CompanyID INT NOT NULL,
    ReportYear INT NOT NULL,
    Environmental_Score DECIMAL(5,2),
    Social_Score DECIMAL(5,2),
    Governance_Score DECIMAL(5,2),
    Final_ESG_score DECIMAL(5,2),
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (CompanyID, ReportYear),
    FOREIGN KEY (CompanyID) REFERENCES company_info(CompanyID)
);

-- Drop the existing esg_finance table if it exists
DROP TABLE IF EXISTS esg_fin;

-- Create the esg_finance table
CREATE TABLE esg_fin (
    CompanyID INT NOT NULL,
	Final_ESG_Score DECIMAL(7, 4) NULL,
    ROE DECIMAL(10,4),
    ROA DECIMAL(10,4),
    DebtToEquity DECIMAL(5,2),
    TotalAssets_thousandsUSD BIGINT,
	Beta DECIMAL(6, 3) NULL,
	Mean_stockprice DECIMAL(10, 2) NULL,
	Yearend_stockprice DECIMAL(10, 2) NULL,
	Currency VARCHAR(255) NULL,
    PRIMARY KEY (CompanyID),
    FOREIGN KEY (CompanyID) REFERENCES company_info(CompanyID)
);

INSERT INTO esg_fin (CompanyID, Final_ESG_Score, ROE, ROA, DebtToEquity, TotalAssets_thousandsUSD, Beta, Mean_stockprice, Yearend_stockprice, Currency) VALUES
(1, NULL, 1.5580, 0.2750, 4.67, 352583000, NULL, NULL, NULL, NULL),
(2, NULL, 0.1975, 0.0281, 6.03, 39256653, NULL, NULL, NULL, NULL),
(3, NULL, 0.1650, 0.0539, 0.97, 45506507, NULL, NULL, NULL, NULL),
(4, NULL, 0.3311, 0.0555, 4.98, 135241000, NULL, NULL, NULL, NULL),
(5, NULL, 0.2552, 0.1703, 0.50, 229623000, NULL, NULL, NULL, NULL),
(6, NULL, 0.0400, 0.0340, 0.25, 349053672, NULL, NULL, NULL, NULL),
(7, NULL, 0.2600, 0.1830, 0.42, 402392000, NULL, NULL, NULL, NULL),
(8, NULL, 0.1351, 0.0748, 0.80, 221370966, NULL, NULL, NULL, NULL);


-- Drop the existing esg_finance table if it exists
DROP TABLE IF EXISTS corr_matrix;

-- Create the corr_matrix table
CREATE TABLE corr_matrix (
	Financial_metric VARCHAR(255) NOT NULL
);

INSERT INTO corr_matrix (Financial_metric) VALUES
('ESG_Score'),
('ROE'),
('ROA'),
('DebtToEquity'),
('TotalAssets_thousandsUSD'),
('Beta')
