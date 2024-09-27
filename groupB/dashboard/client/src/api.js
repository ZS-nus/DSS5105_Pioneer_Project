import axios from 'axios';

const API_BASE_URL = 'http://localhost:5105/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // Add any other default headers here
  },
});

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

  export const fetchEScoreData = () => {
    return api.get('/score/environment');
  };

  export const fetchSScoreData = () => {
    return api.get('/score/social');
  };

  export const fetchGScoreData = () => {
    return api.get('/score/governance');
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
