import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import React, { useState,useEffect } from 'react';
import Login from './Login';
import MainScreen from './MainScreen/MainScreen';
import HomeScreen from './HomeScreen/HomeScreen.jsx';
import LandingScreen from './LandingScreen/LandingScreen.jsx';
import Register from './Register';
import { CurrentUserContext } from './CurrentUserContext.jsx';
import FeaturesDataProvider from './FeaturesDataContext.jsx';

function App() {
  const userObject = {
      userID: null,
      username: null,
      currentProject: {
          projectName: null,
          videoFile: null,
          originalVideoFile: null,
          videoFileUrl: null,
          originalVideoFileUrl: null
      }
  }
  const [currentUser, setCurrentUser] = useState(() => {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      return JSON.parse(savedUser);
    } else {
      return userObject;
    }
  });

  useEffect(() => {
    localStorage.setItem('currentUser', JSON.stringify(currentUser));
  }, [currentUser]);
  
  return (
    <CurrentUserContext.Provider value={{currentUser, setCurrentUser}}>
      <Router>
        <Routes>
        <Route path="/eva" element={<LandingScreen/>} />
          <Route path="/login" element={<Login/>} />
          <Route path="/project" element={
              <FeaturesDataProvider>
                <MainScreen/>
              </FeaturesDataProvider>
          } />
          <Route path="/home" element={<HomeScreen/>/*currentUser.userID !== null ? <HomeScreen/> : <Navigate replace to="/login" />*/} />
          <Route path="/" element={<Navigate replace to="/login" />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={currentUser.userID !== null ? <Navigate replace to="/home" /> : <Navigate replace to="/login" />} />
        </Routes>
      </Router>
    </CurrentUserContext.Provider>
  );
}

export default App;
