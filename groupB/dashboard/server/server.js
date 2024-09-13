const admin = require('firebase-admin');
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');

const serviceAccount = require('../pioneer_key.json');

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
      // Log user information
      console.log('User authenticated:', userRecord);

      // In this case, Firebase Admin doesn't support password authentication
      // You can validate the user based on email or use a third-party system.
      res.status(200).json({ message: 'User authenticated successfully', user: userRecord });
    } else {
      res.status(404).json({ error: 'User not found' });
    }
  } catch (error) {
    console.error('Error during authentication:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});