import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';
import { Link } from 'react-router-dom';
import base_backend_url from './base_backend_url.js';
import backgroundImage from './assets/backgroundtechsmithpattern.jpeg';
import { CurrentUserContext } from './CurrentUserContext';
import LoginLoadingWheel from './components/LoginLoadingWheel.jsx';

/**
 * Login is a functional component that represents the login form of the application.
 *
 */ 
function Login() { 
  const {
    currentUser,
    setCurrentUser
  } = useContext(CurrentUserContext)

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false)
  const [showModal, setShowModal] = useState(false);
  const [modalClass, setModalClass] = useState('modal hidden');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoggingIn(true)
    
    try {
      let destinationUrl = `${base_backend_url}/auth/login/`
      const response = await fetch(destinationUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ "username":username, "password":password }),
      });
    
      const data = await response.json();
    
      if (response.ok) {
        // Save the access token to local storage
        localStorage.setItem('token', data.access_token);
        console.log('Login successful:', data);

        let userObj = {
          userID: -1,
          username: "string",
          currentProject: null
        }

        userObj.userID = data.user_id
        userObj.username = data.user_name

        setCurrentUser(currentUser => ({
          ...currentUser,
          userID: data.user_id,
            username: data.user_name,
            currentProject: null,
          ...userObj
        })); // updating the login state

        navigate('/home', { replace: true }); // navigating to the home page
      } else {
        console.error('Login failed:', data.detail);
        
        if (response.status == 400) {
          setShowModal(true);
        }
      }
    }
    finally{
      setIsLoggingIn(false)
    }
      
  };

  function Modal({ onClose }) {
    return (
      <div className="modal visible">
        <div className="modal-content">
          <h2>Incorrect credentials</h2>
          <p>Please try again.</p>
          <button onClick={onClose}>Close</button>
        </div>
      </div>
    );
  }

  return (
    <div className="login-wrapper">
      {showModal && <Modal onClose={() => setShowModal(false)} />}
      {(isLoggingIn) && <LoginLoadingWheel/>}
      <div className="login-card">
      <div className="login-image-section">
      <img src={backgroundImage} alt="Background" />
      </div>
      <div className="login-form-section">
        <form onSubmit={handleSubmit}>
          <h2>Login</h2>
          <label>
            Username:
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            Password:
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </label>
          <button type="submit">Login</button>
          <div className="login-footer">
            Don't have an account? <Link to="/register">Register here</Link>
          </div>
        </form>
      </div>
      </div>
    </div>
  );
}

export default Login;
