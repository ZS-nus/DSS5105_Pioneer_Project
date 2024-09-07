import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './fonts/icomoon/style.css';
import './css/style.css';
import bgImage from './images/login_bg.jpg';

function Login() {
  return (
    <div className="d-lg-flex half">
      <div className="bg order-1 order-md-2" style={{ backgroundImage: `url(${bgImage})` }}></div>
      <div className="contents order-2 order-md-1">
        <div className="container">
          <div className="row align-items-center justify-content-center">
            <div className="col-md-7">
              <h3>Login to <strong>Pionner Team Project</strong></h3>
              <br></br>
              <form action="#" method="post">
                <div className="form-group first">
                  <label htmlFor="username">Username</label>
                  <input type="text" className="form-control" placeholder="Username" id="username" />
                </div>
                <div className="form-group last mb-3">
                  <label htmlFor="password">Password</label>
                  <input type="password" className="form-control" placeholder="Your Password" id="password" />
                </div>
                <div className="d-flex mb-5 align-items-center">
                  <label className="control control--checkbox mb-0">
                    <span className="caption">Remember me</span>
                    <input type="checkbox" defaultChecked />
                    <div className="control__indicator"></div>
                  </label>
                  {/* <span className="ml-auto">
                    <button className="forgot-pass" onClick={() => alert('Forgot Password clicked!')}>Forgot Password</button>
                  </span> */}
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