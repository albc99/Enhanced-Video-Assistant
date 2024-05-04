import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Register.css'; 
import { Link } from 'react-router-dom';


import base_backend_url from './base_backend_url.js';

/**
 *  Register is a functional component that represents the registration form of the application.
 * 
 *  After registering, they will be able to sign in next time they visit the application.
 * 
 */
function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    const response = await fetch(`${base_backend_url}/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password, email }),
    });
  
    const data = await response.json();
  
    if (response.ok) {
      console.log('Registration successful:', data);
      navigate('/login', { replace: true }); 
    } else {
      console.error('Registration failed:', data.detail);
    }
  };

  return (
    <div className="register-container">
      <form onSubmit={handleSubmit}>
        <h2>Register</h2>
        <label>
          Username:
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label>
          Email:
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Password:
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <button type="submit">Register</button>
        <div className="register-footer">
          Already have an account? <Link to="/login">Login here</Link>
        </div>
      </form>
    </div>
  );
}

export default Register;
