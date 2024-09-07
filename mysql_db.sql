-- Create DESIGNLogin database
CREATE DATABASE pioneerDB;

-- Select the DESIGNLogin database
USE pioneerDB;

-- Create Users table
CREATE TABLE Users (
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);


-- Insert a row into Users table
INSERT INTO Users (username, password) VALUES ('admin', '123456');