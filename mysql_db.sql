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

-- Create env_metrics table
CREATE TABLE env_metrics (
    eco_metrics_id INT AUTO_INCREMENT PRIMARY KEY
);


