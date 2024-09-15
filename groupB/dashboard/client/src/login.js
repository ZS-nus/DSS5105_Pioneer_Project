import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './fonts/icomoon/style.css';
import './css/style.css';
import bgImage from './images/login_bg.jpg';
import axios from 'axios';

function Login({ setIsAuthenticated }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5105/api/login', { email, password });
      console.log('Login successful:', response.data);
      if (response.data && response.data.message) {
        setIsAuthenticated(true);
        localStorage.setItem('isAuthenticated', 'true');
        navigate('/admin');
      } else {
        throw new Error('Unexpected server response');
      }
    } catch (err) {
      console.error('Login failed:', err);
      setError('Failed to log in: ' + (err.response?.data?.error || err.message || 'Unknown error'));
    }
  };

  return (
    <div className="d-lg-flex half">
      <div className="bg order-1 order-md-2" style={{ backgroundImage: `url(${bgImage})` }}></div>
      <div className="contents order-2 order-md-1">
        <div className="container">
          <div className="row align-items-center justify-content-center">
            <div className="col-md-7">
              <h3>Login to <strong>Pioneer Team Project</strong></h3>
              <br></br>
              {error && <div className="alert alert-danger">{error}</div>}
              <form onSubmit={handleSubmit}>
                <div className="form-group first">
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    placeholder="Email"
                    id="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="form-group last mb-3">
                  <label htmlFor="password">Password</label>
                  <input
                    type="password"
                    className="form-control"
                    placeholder="Your Password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                </div>
                <div className="d-flex mb-5 align-items-center">
                  <label className="control control--checkbox mb-0">
                    <span className="caption">Remember me</span>
                    <input type="checkbox" defaultChecked />
                    <div className="control__indicator"></div>
                  </label>
                </div>
                <input type="submit" value="Log In" className="btn btn-block btn-primary" />
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;
