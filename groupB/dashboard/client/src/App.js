import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { ChakraProvider } from '@chakra-ui/react';
import SignIn from './views/auth/signIn';
import AdminLayout from './layouts/admin';
import AuthLayout from './layouts/auth';
import initialTheme from './theme/theme';

function App() {
  const [currentTheme, setCurrentTheme] = React.useState(initialTheme);

  const ProtectedRoute = () => {
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    const isLoggedOut = sessionStorage.getItem('isLoggedOut') === 'true';
    
    if (!isAuthenticated || isLoggedOut) {
      return <Navigate to="/auth/sign-in" replace />;
    }
    
    return <Outlet />;
  };

  return (
    <ChakraProvider theme={currentTheme}>
      <Router>
        <Routes>
          <Route path="/auth" element={<AuthLayout />}>
            <Route path="sign-in" element={<SignIn />} />
            {/* Add other auth routes here if needed */}
          </Route>
          
          <Route element={<ProtectedRoute />}>
            <Route 
              path="/admin/*" 
              element={<AdminLayout theme={currentTheme} setTheme={setCurrentTheme} />} 
            />
          </Route>

          <Route path="/" element={<Navigate to="/auth/sign-in" replace />} />
          <Route path="*" element={<Navigate to="/auth/sign-in" replace />} />
        </Routes>
      </Router>
    </ChakraProvider>
  );
}

export default App;