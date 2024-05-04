import React, { useState,useContext,useEffect,useRef } from 'react';
import DeletedClip from './DeletedClip.jsx'
import './VideoStreamliner.css'
import ReactPlayer from 'react-player';
import { CurrentUserContext } from '../../../CurrentUserContext.jsx';
import base_backend_url from '../../../base_backend_url.js';
import { FeaturesDataContext } from '../../../FeaturesDataContext.jsx';
import Tooltip from '../../../components/tooltip.jsx'

/**
 * VideoStreamliner is a functional component that handles video streamlining.
 *
 */
function VideoStreamliner() {
  const {streamlinerData, setStreamlinerData, setScrubberTimestamps,isLoadingFeatureData, scrubberTimestamps, sources, setSources} = useContext(FeaturesDataContext);
  const [isLoading, setIsLoading] = useState(false);
  const [outputFilePath, setOutputFilepath] = useState(null);
  const {currentUser, setCurrentUser} = useContext(CurrentUserContext)
  const reactPlayerRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [disableBtn, setDisableBtn] = useState(false);
  const [startingTimeInSeconds, setStartingTimeInSeconds] = useState(0);
  const [endingTimeInSeconds, setEndingTimeInSeconds] = useState(0);
  const [duration, setDuration] = useState(0);
  const [initialTimestamps, setInitialTimestamps] = useState([]);

  // Use effect for loading state
  useEffect(() => {
    setIsLoading(isLoadingFeatureData);
  }, [isLoadingFeatureData]);

  // Use effect for setting initial timestamps
  useEffect(() => {
    if (streamlinerData.deleted_clip_timestamps.length > 0) {
      const flattenedTimestamps = [].concat(...streamlinerData.deleted_clip_timestamps);
      setInitialTimestamps(flattenedTimestamps);
      console.log("Initial timestamps:", initialTimestamps);
    }
  }, [streamlinerData.deleted_clip_timestamps]);

    // handleRun is used to fetch the data from the backend
    const handleRun = () => {
      console.log('Before fetch, feedback state is:', streamlinerData);
      console.log('Before fetch, filepath is:', outputFilePath);

      setIsLoading(true);
      fetch(`${base_backend_url}/eva/streamline_video/${currentUser.userID}/${currentUser.currentProject.projectID}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
      })
      .then(response => response.json())
      .then(data => {
        if (data.deleted_clip_timestamps || data.important_clip_timestamps || data.outputFilePath) {
          setStreamlinerData(currentState => ({
              ...currentState,
              deleted_clip_timestamps: data.deleted_clip_timestamps ? data.deleted_clip_timestamps : currentState.deleted_clip_timestamps,
              important_clip_timestamps: data.important_clip_timestamps ? data.important_clip_timestamps : currentState.important_clip_timestamps,
              outputFilePath: data.outputFilePath ? data.outputFilePath : currentState.outputFilePath
          }));
          
      }
        setOutputFilepath(data.outputFilePath);
        setSources(sources => {
          return new Array(data.deleted_clip_timestamps.length).fill("STREAMLINER");
        })

        setScrubberTimestamps(currentTimestamps => {
          return data.deleted_clip_timestamps
        });

      })
      .catch(error => {
        console.error('Error:', error);
      })
      .finally(() => {
        // disable the button once streamliner is ran
        setDisableBtn(true);
        setIsLoading(false); 
      });
    }

    const handleDuration = (dur) => {
      setDuration(dur);
    };
    const undoAllChanges = () => {
      if (initialTimestamps[initialTimestamps.length - 1] === "end") {
        initialTimestamps[initialTimestamps.length - 1] = duration
      }
      setScrubberTimestamps(initialTimestamps);

    };

    // the pause video function is used to pause the video when it reaches the end of the clip
    const pauseVideo = (state) => {
      const currentTime = reactPlayerRef.current.getCurrentTime();

      if (currentTime >= endingTimeInSeconds && isPlaying) {
        setIsPlaying(false);
        reactPlayerRef.current.seekTo(startingTimeInSeconds);
      }
    };

    // play video clip at the specified start time
    const playVideo = (startTime, endTime) => {
      setIsPlaying(true);
      reactPlayerRef.current.seekTo(startTime);
      setStartingTimeInSeconds(startTime);
      setEndingTimeInSeconds(Number(endTime));
      
      
    };

    const renderFeedback = () => {
      if (isLoading) {
        return <div className='loading'></div>;
      }
      if (streamlinerData.deleted_clip_timestamps.length == 0) {
        
        return <p>Streamliner not run yet.</p>;
      }
      
      return (
        
        <div className="vs-feedback-section">
          <div className="vs-feedback-content">
            <div className="vs-video-container">  
            <ReactPlayer
              ref= {reactPlayerRef}
              controls
              onProgress = {pauseVideo}
              onDuration={handleDuration}
              playing = {isPlaying}
              url={currentUser.currentProject.videoURL}
              width='100%'
              height='100%'
            />
            </div>
            <div>
              <h3>Suggested Deleted Clips <Tooltip text="Displays all sugested to be removed clips. ↩ Adds deleted section to timeline."/></h3>
              <div className='deleted-clips-container'>
                {scrubberTimestamps && scrubberTimestamps.length > 0 ? (
                  scrubberTimestamps.map((timestamp, index) => {
                    if (index % 2 === 0) {
                      const startTimestamp = isNaN(timestamp) ? 0 : parseFloat(timestamp);
                      const endTimestamp = index + 1 < scrubberTimestamps.length && !isNaN(scrubberTimestamps[index + 1]) ? parseFloat(scrubberTimestamps[index + 1]) : parseFloat(duration.toFixed(2));
                      
                      return <DeletedClip
                                key={index} 
                                startingTimeInSeconds={startTimestamp}
                                endingTimeInSeconds={endTimestamp}
                                timestampIndex={index}
                                playVideo={playVideo}
                              />
                    }
                    return null;
                  })
                ) : <>
                <p className="message">All clips have been restored!</p>
                <button className="vs-undo-btn" onClick={undoAllChanges}>Undo All Changes</button>
              </>}
              </div>
            </div>
          </div>
        </div>
      );
    };

    return (
      <div className="video-streamliner">
        <h1>Video Streamliner</h1>
        {!isLoading ? (
          <div className="deleted-clip-container">
            {renderFeedback()}
          </div>
        ) : (
          // Loading case 
          <div className="deleted-clip-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
            {renderFeedback()}
          </div>
        )}
        
        <div className='streamliner-sidepanel-top'>
        
        <button className="vs-run-btn" onClick={handleRun} disabled={disableBtn || !currentUser.currentProject.isUploaded || isLoading}title={!currentUser.currentProject.isUploaded ? "Video is uploading..." : "Provides user with clips that can be cut out to streamline the video." }>Suggest Deleted Clips <Tooltip text="Provides user with clips that can be cut out to streamline the video."/></button>        {/* <button className="run-btn" disabled={!currentUser.currentProject.isUploaded}title={!currentUser.currentProject.isUploaded ? "Video is uploading..." : ""}> Manual Cut Mode</button> */}

      </div>
      </div>
    );
  }
  
export default VideoStreamliner; 