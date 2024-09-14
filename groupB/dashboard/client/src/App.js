import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ChakraProvider } from '@chakra-ui/react';
import Login from './login';
import AdminLayout from './layouts/admin';
import initialTheme from './theme/theme';

function App() {
  const [currentTheme, setCurrentTheme] = useState(initialTheme);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check authentication status here (e.g., from localStorage or a token)
    const checkAuth = async () => {
      // Replace this with your actual authentication check
      const auth = localStorage.getItem('isAuthenticated') === 'true';
      setIsAuthenticated(auth);
      setIsLoading(false);
    };
    checkAuth();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>; // Or a loading spinner
  }

  return (
    <ChakraProvider theme={currentTheme}>
      <Router>
        <Routes>
          <Route path="/login" element={
            isAuthenticated ? 
              <Navigate to="/admin" replace /> : 
              <Login setIsAuthenticated={setIsAuthenticated} />
          } />
          <Route
            path="/admin/*"
            element={
              isAuthenticated ? (
                <AdminLayout theme={currentTheme} setTheme={setCurrentTheme} />
              ) : (
                <Navigate to="/login" replace />
              )
            }
          />
          <Route path="/" element={<Navigate to="/admin" replace />} />
          <Route path="*" element={<Navigate to="/admin" replace />} />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;