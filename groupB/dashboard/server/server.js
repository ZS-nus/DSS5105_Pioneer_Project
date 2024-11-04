require('dotenv').config();
const admin = require('firebase-admin');
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const mysql = require('mysql2/promise');
const serviceAccount = require('../pioneer_key.json');
const { Storage } = require('@google-cloud/storage');
const { S3Client, ListObjectsV2Command } = require('@aws-sdk/client-s3');
const multer = require('multer');
const upload = multer({ storage: multer.memoryStorage() });
const axios = require('axios');

// Create an S3 client without specifying credentials
const s3Client = new S3Client({
  region: 'ap-southeast-1' // Your AWS region
});

// Update the dbConfig object
const dbConfig = {
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT, 10),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
};

let pool;

function logConnectionDetails() {
  console.log('Database Config:', {
    host: dbConfig.host,
    port: dbConfig.port,
    user: dbConfig.user,
    database: dbConfig.database
  });
}

async function createDirectConnection() {
  try {
    console.log('Attempting direct database connection...');
    // logConnectionDetails();
    pool = mysql.createPool(dbConfig);
    await pool.getConnection();
    console.log('Successfully connected to the database directly.');
    return true;
  } catch (error) {
    console.error('Direct connection failed:', error.message);
    return false;
  }
}

async function createSSLConnection() {
  try {
    console.log('Attempting SSL database connection...');
    // logConnectionDetails();
    const sslConfig = {
      ...dbConfig,
      ssl: {
        rejectUnauthorized: false,
        key: Buffer.from(process.env.SSL_KEY_BASE64, 'base64').toString('ascii')
      }
    };
    if (process.env.SSL_KEY_BASE64) {
      sslConfig.ssl.key = Buffer.from(process.env.SSL_KEY_BASE64, 'base64').toString('ascii');
    }
    pool = mysql.createPool(sslConfig);
    await pool.getConnection();
    console.log('Successfully connected to the database through SSL.');
    return true;
  } catch (error) {
    console.error('SSL connection failed:', error.message);
    return false;
  }
}

async function createTunnel() {
  try {
    if (await createDirectConnection()) return true;
    if (await createSSLConnection()) return true;
    return false;
  } catch (error) {
    console.error('All connection methods failed:', error);
    return false;
  }
}

async function reconnect() {
  console.log('Attempting to reconnect...');
  if (pool) {
    await pool.end().catch(err => console.error('Error closing pool:', err.message));
  }
  return createTunnel();
}

async function executeQuery(query, params = []) {
  const maxRetries = 3;
  let retries = 0;

  while (retries < maxRetries) {
    try {
      if (!pool) {
        await reconnect();
      }
      const [rows] = await pool.query({
        sql: query,
        timeout: 30000, // 30 seconds
      }, params);
      return rows;
    } catch (error) {
      console.error(`Error executing query (attempt ${retries + 1}):`, error.message);
      retries++;
      if (retries === maxRetries) {
        throw error;
      }
      await reconnect();
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

function getCurrentDateTime() {
  const now = new Date();
  const utcOffset = 8 * 60; // UTC +8 in minutes
  const localDate = new Date(now.getTime() + utcOffset * 60 * 1000); // Adjust for UTC +8
  return localDate.toISOString(); // Returns the date and time in ISO format
}

async function keepTryingToConnect() {
  while (true) {
    const success = await createTunnel();
    if (success) {
      console.log(`${getCurrentDateTime()} - Database connection established.`);
      // Start keep-alive mechanism
      setInterval(() => {
        if (pool) {
          pool.query('SELECT 1')
            .then(() => console.log(`${getCurrentDateTime()} - Keep-alive query executed successfully`))
            .catch(err => console.error(`${getCurrentDateTime()} - Keep-alive query failed:`, err.message));
        }
      }, 60000); // Run every 60 seconds
      break;
    } else {
      console.log(`${getCurrentDateTime()} - Retrying database connection in 5 seconds...`);
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
}

// Update the initialization to include the storage bucket
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  storageBucket: process.env.STORAGE_BUCKET
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
  app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
  });

  // Start trying to connect to the database
  keepTryingToConnect();
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

// Modify the /api/table/environment endpoint
app.get('/api/table/financial', async (req, res) => {
  try {
    console.log('Fetching financial data...');
    const query = `
      SELECT 
        c.CompanyName,
        f.CompanyID,
        ROUND(f.Final_ESG_Score, 2) AS Final_ESG_Score,
        ROUND(f.ROE, 2) AS ROE,
        ROUND(f.ROA, 2) AS ROA,
        ROUND(f.DebtToEquity, 2) AS DebtToEquity,
        f.TotalAssets_thousandsUSD,
        ROUND(f.Beta, 3) AS Beta,
        ROUND(f.Mean_stockprice, 2) AS Mean_stockprice,
        ROUND(f.Yearend_stockprice, 2) AS Yearend_stockprice,
        f.Currency
      FROM esg_fin f
      INNER JOIN company_info c ON f.CompanyID = c.CompanyID
      ORDER BY c.CompanyName
    `;

    const rows = await executeQuery(query);
    
    if (rows.length > 0) {
      console.log('First financial data row:', rows[0]);
      res.json(rows);
    } else {
      console.log('No financial data found.');
      res.status(404).json({ error: 'No data found' });
    }
  } catch (error) {
    console.error('Error fetching financial data:', error);
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
        s.DataSecurity,
        s.CustomerPrivacy,
        s.Cybersecurity,
        ROUND(s.MalePercentage, 2) AS MalePercentage,
        ROUND(s.FemalePercentage, 2) AS FemalePercentage,
        ROUND(s.TrainingHours, 1) AS TrainingHours,
        s.WorkRelatedInjuries
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

// Add this new endpoint for governance data
app.get('/api/table/governance', async (req, res) => {
  try {
    console.log('Fetching governance data...');
    const query = `
      SELECT 
        c.CompanyName,
        g.CompanyID,
        g.ReportYear,
        g.BoardComposition,
        g.EthicalBehaviour,
        g.RiskManagement,
        g.CertificationList
      FROM governance g
      INNER JOIN company_info c ON g.CompanyID = c.CompanyID
      INNER JOIN (
        SELECT CompanyID, MAX(ReportYear) as LatestYear
        FROM governance
        GROUP BY CompanyID
      ) latest ON g.CompanyID = latest.CompanyID AND g.ReportYear = latest.LatestYear
      ORDER BY c.CompanyName
    `;

    const rows = await executeQuery(query);
    
    if (rows.length > 0) {
      console.log('First governance data row:', rows[0]);
      res.json(rows);
    } else {
      console.log('No governance data found.');
      res.status(404).json({ error: 'No data found' });
    }
  } catch (error) {
    console.error('Error fetching governance data:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Add this new endpoint to list files in S3 and fallback to Firebase Storage
app.get('/api/s3/storage/files', async (req, res) => {
  const params = {
    Bucket: 'rg-dss5105project1-pioneers3-648' // Updated S3 bucket name
  };

  try {
    const command = new ListObjectsV2Command(params);
    const data = await s3Client.send(command);
    const fileList = data.Contents.map(file => ({
      name: file.Key,
      downloadUrl: `https://${params.Bucket}.s3.amazonaws.com/${file.Key}` // Generate a public URL for downloading
    }));

    // If files are found in S3, return them
    if (fileList.length > 0) {
      return res.json(fileList);
    } else {
      throw new Error('No files found in S3');
    }
  } catch (error) {
    // console.error('Error fetching files from S3:', error);
    
    // Fallback to Firebase Storage
    try {
      const bucket = admin.storage().bucket();
      const [files] = await bucket.getFiles({ prefix: 'reports/' }); // Specify the prefix to fetch files from the reports folder
      const firebaseFileList = files.map(file => {
        const fileNameWithoutPrefix = file.name.replace('reports/', ''); // Remove the 'reports/' prefix
        return {
          name: fileNameWithoutPrefix, // Use the modified name
          downloadUrl: `https://firebasestorage.googleapis.com/v0/b/${process.env.STORAGE_BUCKET}/o/${encodeURIComponent(file.name)}?alt=media`
        };
      });

      // Log the firebaseFileList to the console
      // console.log('Files fetched from Firebase Storage:', firebaseFileList);

      // Return files from Firebase Storage
      return res.json(firebaseFileList);
    } catch (firebaseError) {
      console.error('Error fetching files from Firebase Storage:', firebaseError);
      return res.status(500).json({ error: 'Internal server error' });
    }
  }
});

// Placeholder function for calling the Python API
async function callPythonExtractionAPI(fileName) {
    const pythonAPIUrl = process.env.PYTHON_Extraction_API_URL;
    
    try {
        // First call the fetch endpoint to process the PDF
        const fetchResponse = await axios.post(`${pythonAPIUrl}/reports/fetch/${encodeURIComponent(fileName)}`);
        console.log('Python API fetch response:', fetchResponse.data);

        if (fetchResponse.data.status === 'success') {
            // If fetch was successful, call the extract endpoint
            const extractResponse = await axios.post(
                `${pythonAPIUrl}/reports/extract/text/${encodeURIComponent(fileName)}`
            );
            console.log('Python API extract response:', extractResponse.data);
            return extractResponse.data;
        } else {
            throw new Error('Failed to fetch and process the PDF');
        }
    } catch (error) {
        console.error('Error calling Python API:', error);
        throw error;
    }
}


// This api is for uploading the report to Firebase
app.post('/api/firebase/upload', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  const file = req.file;
  const now = new Date();
  const dateString = now.getFullYear() +
                     ('0' + (now.getMonth() + 1)).slice(-2) +
                     ('0' + now.getDate()).slice(-2) +
                     '_' +
                     ('0' + now.getHours()).slice(-2) +
                     ('0' + now.getMinutes()).slice(-2) +
                     ('0' + now.getSeconds()).slice(-2);
  
  const fileName = `reports/${dateString}_${file.originalname}`;
  console.log("File selected for upload", fileName);

  try {
    const bucket = admin.storage().bucket();
    const fileUpload = bucket.file(fileName);

    const blobStream = fileUpload.createWriteStream({
      metadata: {
        contentType: file.mimetype
      }
    });

    blobStream.on('error', (error) => {
      console.error('Error uploading file:', error);
      res.status(500).send('Error uploading file.');
    });

    blobStream.on('finish', async () => {
      // Make the file publicly accessible
      await fileUpload.makePublic();

      const publicUrl = `https://storage.googleapis.com/${bucket.name}/${fileUpload.name}`;
      
      // Call the Python API
      try {
        const pythonAPIResponse = await callPythonExtractionAPI(fileName);
        res.status(200).send({ 
          message: 'File uploaded successfully and processed', 
          url: publicUrl,
          pythonAPIResponse 
        });
      } catch (pythonAPIError) {
        console.error('Error from Python API:', pythonAPIError);
        res.status(200).send({ 
          message: 'File uploaded successfully, but processing failed', 
          url: publicUrl,
          error: 'PDF processing failed'
        });
      }
    });

    blobStream.end(file.buffer);
  } catch (error) {
    console.error('Error in file upload:', error);
    res.status(500).send('Server error during file upload.');
  }
});

process.on('SIGINT', async () => {
  console.log('Shutting down gracefully...');
  if (pool) {
    await pool.end();
  }
  process.exit(0);
});

// Corrected endpoint for ESG scores
app.get('/api/score/esg', async (req, res) => {
  try {
    console.log('Fetching ESG scores...');
    const query = `
      SELECT 
        c.CompanyName,
        e.CompanyID,
        e.ReportYear,
        e.Environmental_Score,
        e.Social_Score,
        e.Governance_Score,
        e.Final_ESG_score
      FROM esg_scores e
      INNER JOIN company_info c ON e.CompanyID = c.CompanyID
      INNER JOIN (
        SELECT CompanyID, MAX(ReportYear) as LatestYear
        FROM esg_scores
        GROUP BY CompanyID
      ) latest ON e.CompanyID = latest.CompanyID AND e.ReportYear = latest.LatestYear
      ORDER BY c.CompanyName
    `;

    const rows = await executeQuery(query);
    
    if (rows.length > 0) {
      console.log('First ESG score row:', rows[0]);
      res.json(rows);
    } else {
      console.log('No ESG scores found.');
      res.status(404).json({ error: 'No data found' });
    }
  } catch (error) {
    console.error('Error fetching ESG scores:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Add this new endpoint for fetching all ESG scores with company info
app.get('/api/dashboard/esg', async (req, res) => {
  try {
    console.log('Fetching all ESG scores with company info...');
    const query = `
      SELECT 
        c.CompanyName,
        e.CompanyID,
        e.ReportYear,
        ROUND(e.Environmental_Score, 2) AS Environmental_Score,
        ROUND(e.Social_Score, 2) AS Social_Score,
        ROUND(e.Governance_Score, 2) AS Governance_Score,
        ROUND(e.Final_ESG_score, 2) AS Final_ESG_score
      FROM esg_scores e
      INNER JOIN company_info c ON e.CompanyID = c.CompanyID
      ORDER BY c.CompanyName, e.ReportYear DESC
    `; // Query to select all records from esg_scores with company info, scores rounded to 2 decimal places
    const rows = await executeQuery(query);
    
    if (rows.length > 0) {
      console.log('Fetched ESG scores:', rows[0]); // Log only the first row to avoid cluttering the console
      res.json(rows);
    } else {
      console.log('No ESG scores found.');
      res.status(404).json({ error: 'No data found' });
    }
  } catch (error) {
    console.error('Error fetching ESG scores:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Add this new endpoint for fetching ESG predictions
app.get('/api/score/predict', async (req, res) => {
  try {
    console.log('Fetching ESG predictions...');
    const query = `
      SELECT 
        c.CompanyName,
        p.CompanyID,
        p.Year,
        ROUND(p.Environmental, 2) AS Environmental_Score,
        ROUND(p.Social, 2) AS Social_Score,
        ROUND(p.Governance, 2) AS Governance_Score,
        ROUND(p.ESG_Score, 2) AS ESG_score,
        p.Data_Type
      FROM esg_predictions p
      INNER JOIN company_info c ON p.CompanyID = c.CompanyID
      ORDER BY c.CompanyName, p.Year
    `;

    const rows = await executeQuery(query);
    
    if (rows.length > 0) {
      console.log('First ESG prediction row:', rows[0]);
      res.json(rows);
    } else {
      console.log('No ESG predictions found.');
      res.status(404).json({ error: 'No data found' });
    }
  } catch (error) {
    console.error('Error fetching ESG predictions:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});
