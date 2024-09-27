require('dotenv').config();
const mysql = require('mysql2/promise');
const fs = require('fs');
const { Client } = require('ssh2');

const sshConfig = {
  host: process.env.DB_HOST,
  port: 22,
  username: 'ec2-user',
  privateKey: fs.readFileSync(process.env.SSL_KEY_PATH)
};

const dbConfig = {
  host: '127.0.0.1', // Connect to MySQL through SSH tunnel
  port: 3306,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME
};

async function connectWithSSHTunnel() {
  return new Promise((resolve, reject) => {
    const sshClient = new Client();
    sshClient.on('ready', () => {
      sshClient.forwardOut(
        '127.0.0.1',
        0,
        '172.31.43.179', // EC2 instance's private IP
        3306,
        async (err, stream) => {
          if (err) reject(err);
          
          const connection = await mysql.createConnection({
            ...dbConfig,
            stream
          });

          resolve({ connection, sshClient });
        }
      );
    }).connect(sshConfig);
  });
}

async function testConnection() {
  try {
    console.log('SSH Config:', { ...sshConfig, privateKey: 'REDACTED' });
    console.log('DB Config:', { ...dbConfig, password: 'REDACTED' });
    console.log('Attempting to connect to the database through SSH tunnel...');
    const { connection, sshClient } = await connectWithSSHTunnel();
    console.log('Successfully connected to the database.');
    
    const [rows] = await connection.execute('SHOW DATABASES');
    console.log('Databases:', rows.map(row => row.Database));

    const [tables] = await connection.execute('SHOW TABLES');
    console.log('Tables in the current database:', tables.map(table => Object.values(table)[0]));

    await connection.end();
    sshClient.end();
  } catch (error) {
    console.error('Error:', error);
  }
}

testConnection();