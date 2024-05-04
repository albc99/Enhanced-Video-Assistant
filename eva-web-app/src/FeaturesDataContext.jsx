import React, { useState, createContext,useRef,useEffect,useContext } from 'react';
import { CurrentUserContext } from './CurrentUserContext';
import base_backend_url from './base_backend_url.js';

// Create a context to make feature data available to all child components of MainScreen
export const FeaturesDataContext = createContext(null);

// Create a provider component
function FeaturesDataProvider({ children }) {
  const stateRef = useRef();
  const {currentUser, setCurrentUser} = useContext(CurrentUserContext); 
  const [streamlinerData, setStreamlinerData] = useState({
    inputFile: "",
    outputFilePath: "",
    deleted_clip_timestamps: [],
    important_clip_timestamps: []
  });

  const [narrationImproverData, setNarrationImproverData] = useState({
      edits: []
  });



  const [focusGroupData, setFocusGroupData] = useState({

      feedback: [],
      clip_tones: [],
      tone_feedback: {tone_score: null, tone_tips: null},
  });

  // current manually edited version data
  // timestamps of the current version of scrubber (manuall editing)
  const [scrubberTimestamps, setScrubberTimestamps] = useState([]);

  const[sources, setSources] = useState([]);

  // timestamps of all selected options (chose by user on clicking more play options button)
  //timestamps of sections that are currently being played in video
  const [currentSelectedOptionsTimestamps, setCurrentSelectedOptionsTimestamps] = useState([]);

  const [chatMessages, setChatMessages] = useState([]);
  //handleLoaddata
  const [isLoadingFeatureData, setIsLoadingFeatureData] = useState(false);
  const value = {
    streamlinerData,
    setStreamlinerData,
    narrationImproverData,
    setNarrationImproverData,
    focusGroupData,
    setFocusGroupData,
    scrubberTimestamps,
    setScrubberTimestamps,
    currentSelectedOptionsTimestamps,
    setCurrentSelectedOptionsTimestamps,
    isLoadingFeatureData,
    setIsLoadingFeatureData,
    chatMessages,
    setChatMessages,
    sources,
    setSources
  };

    async function autoHandleSaveData() {
      console.log("Save");
      const x = ({"projectID" : currentUser.currentProject.projectID})
      fetch(`${base_backend_url}/projects/save_project/${currentUser.userID}/${currentUser.currentProject.projectID}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({ 
          "scrubber_timestamps" : scrubberTimestamps
      }),
      })
      .then(response => response.json())
      .then(data => {
          console.log(data);  
      })
      .catch(error => {
          console.error('Error:', error);
      })   
      .finally(() => {
          console.log("Data saved")
      });
  }


  useEffect(() => {
      // Update stateRef.current with the latest state
      stateRef.current = {streamlinerData, narrationImproverData, focusGroupData};
  }, [streamlinerData, narrationImproverData, focusGroupData]);

  useEffect(() => {
      return async () => {
          console.log("Unloading FeaturesDataProvider and saving data");
          // await autoHandleSaveData();
      };
  }, []);
  return <FeaturesDataContext.Provider value={value}>{children}</FeaturesDataContext.Provider>;
}

export default FeaturesDataProvider;