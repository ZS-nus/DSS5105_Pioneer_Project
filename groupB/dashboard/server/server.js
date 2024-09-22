require('dotenv').config();
const admin = require('firebase-admin');
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const mysql = require('mysql2/promise');
const serviceAccount = require('../pioneer_key.json');

// Update the dbConfig object
const dbConfig = {
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT, 10),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  ssl: process.env.SSL_KEY_BASE64
    ? {
        rejectUnauthorized: false,
        key: Buffer.from(process.env.SSL_KEY_BASE64, 'base64').toString('ascii')
      }
    : false,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

let pool;

// Modify the createTunnel function
async function createTunnel() {
  try {
    console.log('Creating database connection...');
    pool = mysql.createPool(dbConfig);
    
    // Test the connection
    const connection = await pool.getConnection();
    console.log('Successfully connected to the database through SSL.');
    connection.release();
    return true;
  } catch (error) {
    console.error('Error connecting to the database:', error);
    return false;
  }
}

// Update the testDatabaseConnection function
async function testDatabaseConnection() {
  try {
    const success = await createTunnel();
    return success;
  } catch (error) {
    console.error('Error connecting to the database:', error);
    return false;
  }
}

// Add a function to handle database queries with retries
async function executeQuery(query, params = []) {
  const maxRetries = 3;
  let retries = 0;

  while (retries < maxRetries) {
    try {
      const [rows] = await pool.query(query, params);
      return rows;
    } catch (error) {
      console.error(`Error executing query (attempt ${retries + 1}):`, error);
      retries++;
      if (retries === maxRetries) {
        throw error;
      }
      // Wait for 1 second before retrying
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const app = express();
const PORT = process.env.PORT || 5105; 

app.use(cors());
app.use(bodyParser.json());

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

app.post('/api/logout', (req, res) => {
  res.status(200).json({ message: 'Logged out successfully' });
});

async function startServer() {
  try {
    const success = await testDatabaseConnection();
    if (success) {
      app.listen(PORT, () => {
        console.log(`Server running on port ${PORT}`);
      });
    } else {
      console.log('Failed to connect to the database. Server not started.');
      process.exit(1);
    }
  } catch (error) {
    console.error('Error starting server:', error);
    process.exit(1);
  }
}

startServer();

// Modify the /api/table/company endpoint
app.get('/api/table/company', async (req, res) => {
  try {
    console.log('Fetching companies data...');
    const rows = await executeQuery('SELECT * FROM company_info');
    if (rows.length > 0) {
      console.log('First company data row:', rows[0]);
    } else {
      console.log('No company data found.');
    }
    res.json(rows);
  } catch (error) {
    console.error('Error fetching companies:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Modify the /api/table/environment endpoint
app.get('/api/table/environment', async (req, res) => {
  try {
    console.log('Fetching environmental data...');
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

    const rows = await executeQuery(query);
    
    if (rows.length > 0) {
      console.log('First environmental data row:', rows[0]);
      res.json(rows);
    } else {
      console.log('No environmental data found.');
      res.status(404).json({ error: 'No data found' });
    }
  } catch (error) {
    console.error('Error fetching environmental data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Add this new endpoint for social data
app.get('/api/table/social', async (req, res) => {
  try {
    console.log('Fetching social data...');
    const query = `
      SELECT 
        c.CompanyName,
        s.CompanyID,
        s.ReportYear,
        s.EmployeeCount,
        ROUND(s.MalePercentage, 2) AS MalePercentage,
        ROUND(s.FemalePercentage, 2) AS FemalePercentage,
        ROUND(s.AgeUnder30, 2) AS AgeUnder30,
        ROUND(s.Age30to50, 2) AS Age30to50,
        ROUND(s.AgeAbove50, 2) AS AgeAbove50,
        ROUND(s.TrainingHours, 1) AS TrainingHours,
        ROUND(s.CommunityInvestmentUSD) AS CommunityInvestmentUSD
      FROM social s
      INNER JOIN company_info c ON s.CompanyID = c.CompanyID
      INNER JOIN (
        SELECT CompanyID, MAX(ReportYear) as LatestYear
        FROM social
        GROUP BY CompanyID
      ) latest ON s.CompanyID = latest.CompanyID AND s.ReportYear = latest.LatestYear
      ORDER BY c.CompanyName
    `;

    const rows = await executeQuery(query);
    
    if (rows.length > 0) {
      console.log('First social data row:', rows[0]);
      res.json(rows);
    } else {
      console.log('No social data found.');
      res.status(404).json({ error: 'No data found' });
    }
  } catch (error) {
    console.error('Error fetching social data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Modify the /api/score/environment endpoint
app.get('/api/score/environment', async (req, res) => {
  try {
    console.log('Fetching environmental score ...');
    const query = `
      SELECT 
        c.CompanyName,
        e.ReportYear,
        ROUND(e.env_score_weighted,2) AS env_score_weighted
      FROM e_score e
      INNER JOIN company_info c ON e.CompanyID = c.CompanyID
    `;
    const rows = await executeQuery(query);
    if (rows.length > 0) {
      console.log('First e_score data row:', rows[0]);
    } else {
      console.log('No e_score data found.');
    }
    res.json(rows);
  } catch (error) {
    console.error('Error fetching e_score:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

process.on('SIGINT', async () => {
  console.log('Shutting down gracefully...');
  if (pool) {
    await pool.end();
  }
  process.exit(0);
});