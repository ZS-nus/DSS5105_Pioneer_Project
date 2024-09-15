const admin = require('firebase-admin');
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const mysql = require('mysql2/promise');
const fs = require('fs').promises;


const serviceAccount = require('../pioneer_key.json');

// MySQL connection
const pool = mysql.createPool({
  host: 'localhost',  // Remove the port from here
  port: 3306,         // Add port as a separate property
  user: 'root',
  password: 'siusing98',
  database: 'pioneerDB',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const app = express();
const PORT = process.env.PORT || 5105; 

app.use(cors());
app.use(bodyParser.json());

// Route for Firebase Authentication
app.post('/api/login', async (req, res) => {
  const { email } = req.body;

  try {
    const userRecord = await admin.auth().getUserByEmail(email);
    if (userRecord) {
      console.log('User authenticated:', userRecord);
      res.status(200).json({ message: 'User authenticated successfully', user: userRecord });
    } else {
      res.status(404).json({ error: 'User not found' });
    }
  } catch (error) {
    console.error('Error during authentication:', error);
    res.status(500).json({ error: error.message });
  }
});

// Add this route to your existing server.js file
app.post('/api/logout', (req, res) => {

  // Example response
  res.status(200).json({ message: 'Logged out successfully' });
});

async function testDatabaseConnection() {
  try {
    const connection = await pool.getConnection();
    console.log('Successfully connected to the database.');
    connection.release();
    return true;
  } catch (error) {
    console.error('Error connecting to the database:', error);
    return false;
  }
}

// Test the connection before starting the server
testDatabaseConnection().then((success) => {
  if (success) {
    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  } else {
    console.log('Failed to connect to the database. Server not started.');
    process.exit(1);
  }
});

// Fetch companies data
app.get('/api/table/company', async (req, res) => {
  try {
    const [rows] = await pool.query('SELECT * FROM company_info');
    res.json(rows);
  } catch (error) {
    console.error('Error fetching companies:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Fetch latest environmental data for each company
app.get('/api/table/environment', async (req, res) => {
  try {
    const query = `
      SELECT 
        c.CompanyName,
        e.CompanyID,
        e.ReportYear,
        ROUND(e.EnergyConsumption) AS EnergyConsumption,
        ROUND(e.GHGEmissions) AS GHGEmissions,
        ROUND(e.WaterUsage) AS WaterUsage,
        ROUND(e.WasteGenerated) AS WasteGenerated,
        ROUND(e.RenewableEnergyUse) AS RenewableEnergyUse
      FROM environment e
      INNER JOIN company_info c ON e.CompanyID = c.CompanyID
      INNER JOIN (
        SELECT CompanyID, MAX(ReportYear) as LatestYear
        FROM environment
        GROUP BY CompanyID
      ) latest ON e.CompanyID = latest.CompanyID AND e.ReportYear = latest.LatestYear
      ORDER BY c.CompanyName
    `;

    const [rows] = await pool.query(query);
    res.json(rows);
  } catch (error) {
    console.error('Error fetching environmental data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// app.listen(PORT, () => {
//   console.log(`Server running on port ${PORT}`);
// });