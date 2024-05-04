import React, { useContext, useState, useEffect } from 'react';
import TopBar from './TopBar/TopBar.jsx'
import VideoViewport from "./Viewport/VideoViewport.jsx";
import SidePanel from "./SidePanels/SidePanel.jsx";
import VideoStreamliner from "./Features/Streamliner/VideoStreamliner.jsx";
import NarrationImprover from "./Features/NarrationImprover/NarrationImprover.jsx";
import FocusGroup from "./Features/FocusGroup/FocusGroup.jsx";
import { CurrentUserContext } from '../CurrentUserContext.jsx';
import base_backend_url from '../base_backend_url.js';
import './MainScreen.css';
import {FeaturesDataContext} from '../FeaturesDataContext.jsx';
import ProgressWheel from '.././components/ProgressWheel.jsx';




function MainScreen({ setIsLoggedIn }) {
    const [activeTab, setActiveTab] = useState('streamliner');
    const {currentUser, setCurrentUser} = useContext(CurrentUserContext); 
    const {  setStreamlinerData,setNarrationImproverData, setFocusGroupData,setIsLoadingFeatureData, isLoadingFeatureData } = useContext(FeaturesDataContext);

    useEffect(() => {
        console.log('Component mounted!');
        console.log("User:", currentUser)

        handleLoadProject();
    },[]);

    const handleTabChange = (tab) => {
        setActiveTab(tab);
    };



    async function handleLoadProject() {
        
        if (currentUser.userID && currentUser.currentProject.projectID) {
            console.log("AAAA")
            console.log((currentUser.currentProject.videoSize)/6000)
            setIsLoadingFeatureData(true);
            return fetch(`${base_backend_url}/projects/load_project/${currentUser.userID}/${currentUser.currentProject.projectID}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            })
            .then(response => response.json())
            .then(data => {

                {data.narrationImproverData && data.narrationImproverData.edits && (setNarrationImproverData(currentState => ({
                    ...currentState,
                    edits: data.narrationImproverData.edits
                })))}
                
                {data.focusGroupData && data.focusGroupData.feedback && data.focusGroupData.clip_tones && (setFocusGroupData(currentState => ({
                    ...currentState,
                    feedback: data.focusGroupData.feedback,
                    clip_tones: data.focusGroupData.clip_tones
                })))}
                
                {data.streamlinerData && data.streamlinerData.deleted_clip_timestamps && data.streamlinerData.important_clip_timestamps && (setStreamlinerData(currentState => ({
                    ...currentState,
                    deleted_clip_timestamps: data.streamlinerData.deleted_clip_timestamps,
                    important_clip_timestamps: data.streamlinerData.important_clip_timestamps,
                })))}
                setCurrentUser(currentUser => ({
                    ...currentUser,
                    currentProject: {
                        ...currentUser.currentProject,
                        isUploaded: true
                    }}))
            })
            .catch(error => {
                console.error('Error:', error);
            })   
            .finally(() => {
                console.log("Saved data successfully")
                setIsLoadingFeatureData(false);
            });
        }else{
            console.log("No user ID or project ID")
        }
    };


    async function downloadVideoOnBackend(){
        console.log(currentUser.currentProject)
        return fetch(`${base_backend_url}/azure_blob/download_video`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
              },
            body: JSON.stringify({ "url":currentUser.currentProject.videoURL, "name"  : currentUser.currentProject.projectID}),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);  
                setCurrentUser(currentUser => ({
                    ...currentUser,
                    currentProject: {
                        ...currentUser.currentProject,
                        isUploaded: true
                    }
                }))
            })
            .catch(error => {
                console.error('Error:', error);
            })  
    }

    return (
      
        <>
        {isLoadingFeatureData ? 
        (
        <div className='mainscreen-container disableInteraction'>
            <div className='loading-wheel-container'>
                {/* <ProgressWheel durationInSeconds={currentUser.currentProject.videoFile.size}/> */}
                {/* <LoadingWheel text="Processing Video" className='loading-wheel' /> */}
                <ProgressWheel durationInSeconds={(currentUser.currentProject.videoSize)/180000} />
            </div>
            <div className="loadingGreyOut"/>

            <div className='left-container'>
                <div className='topbar-container'>
                    <TopBar setIsLoggedIn={setIsLoggedIn} onTabChange={handleTabChange} />
                </div>
                <VideoViewport activeTab={activeTab} url={currentUser.currentProject.videoURL}/>

            
            </div>
        
            <div className="right-container">
                <SidePanel>
                    {activeTab === 'streamliner' && <VideoStreamliner  />}
                    {activeTab === 'narrator' && <NarrationImprover />}
                    {activeTab === 'focus' && <FocusGroup />}
                </SidePanel>
            </div>

        </div>
        
        ) : (
        <div className='mainscreen-container'>
            <div className='left-container'>
                <div className='topbar-container'>
                    <TopBar setIsLoggedIn={setIsLoggedIn} onTabChange={handleTabChange} />
                </div>
                <VideoViewport activeTab={activeTab} url={currentUser.currentProject.videoURL}/>

            
            </div>
           
            <div className="right-container">
                <SidePanel>
                    {activeTab === 'streamliner' && <VideoStreamliner  />}
                    {activeTab === 'narrator' && <NarrationImprover />}
                    {activeTab === 'focus' && <FocusGroup />}
                </SidePanel>
            </div>
        </div>


        )


        }
        
        </>
    );
}
export default MainScreen;