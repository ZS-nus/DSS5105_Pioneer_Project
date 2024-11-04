import axios from 'axios';

const API_BASE_URL = 'http://localhost:5105/api';
const PYTHON_API_BASE_URL = 'http://localhost:5106';  // New Python API base URL

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // Add any other default headers here
  },
});

// Create a new axios instance for the Python API
const pythonApi = axios.create({
  baseURL: PYTHON_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // Add any other default headers here
  },
});

// Add this new function for fetching ESG commentary from the Python API
export const fetchESGCommentary = (companyId) => {
  return pythonApi.get(`/dashboard/analysis/${companyId}`);
};

export const loginUser = (credentials) => {
  return api.post('/login', credentials);
};

export const fetchGovernanceData = () => {
    return api.get('/table/governance');
  };

  export const fetchCompanyData = () => {
    return api.get('/table/company');
  };

  export const fetchEnvironmentalData = () => {
    return api.get('/table/environment');
  };

  export const fetchSocialData = () => {
    return api.get('/table/social');
  };

  export const fetchFinancialData = () => {
    return api.get('/table/financial');
  };


  export const fetchEScoreData = () => {
    return api.get('/score/environment');
  };

  export const fetchSScoreData = () => {
    return api.get('/score/social');
  };

  export const fetchGScoreData = () => {
    return api.get('/score/governance');
  };

  export const fetchESGScoreData = () => {
    return api.get('/score/esg');
  };

  export const fetchESGPredict = () => {
    return api.get('/score/predict');
  };


  export const fetchDashboardESGData = () => {
    return api.get('/dashboard/esg');
  };

  export const fetchFirebaseStorageFiles = () => {
    return api.get('/s3/storage/files');
  };


  export const reportUploadToFirebase = async (formData) => {
    try {
      const response = await api.post('/firebase/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error in reportUploadToFirebase:', error);
      throw error;
    }
  };

  // export const reportUploadToS3 = () => {
  //   return api.get('/s3/upload');
  // };


// Add other API calls as needed

export default api;
