import React, {useContext, useState, useRef, useEffect } from 'react';
import './NarrationImprover.css';
import { CurrentUserContext } from '../../../CurrentUserContext.jsx';
import Original from './Original.jsx';
import base_backend_url from '../../../base_backend_url.js';import ReactPlayer from 'react-player';
import Tooltip from '../../../components/tooltip.jsx'
import { FeaturesDataContext } from '../../../FeaturesDataContext';

/**
 * NarrationImprover is a functional component that handles the narration improvement feature of the application.
 *
 */
function NarrationImprover() {
  const {narrationImproverData, setNarrationImproverData, scrubberTimestamps, setScrubberTimestamps, isLoadingFeatureData, sources, setSources} = useContext(FeaturesDataContext);
  const [isLoading, setIsLoading] = useState(false);
  const [disableBtn, setDisableBtn] = useState(false);
  const reactPlayerRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [startingTimeInSeconds, setStartingTimeInSeconds] = useState(0);
  const [endingTimeInSeconds, setEndingTimeInSeconds] = useState(0);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    setIsLoading(isLoadingFeatureData);
  }, [isLoadingFeatureData]);

  const {currentUser, setCurrentUser} = useContext(CurrentUserContext)

    // play video clip at the specified start time
    const playVideo = (startTime, endTime, offset) => {
      setIsPlaying(true);
      reactPlayerRef.current.seekTo(startTime);
      setStartingTimeInSeconds(startTime);
      setEndingTimeInSeconds(endTime);
      setOffset(offset)
    };
    const skipAhead = () => {
      const currentTime = reactPlayerRef.current.getCurrentTime();
      if(currentTime >= endingTimeInSeconds){
        setIsPlaying(false);
        reactPlayerRef.current.seekTo(startingTimeInSeconds)
      }
      };

  const handleGenerate = () => {
    setIsLoading(true);
    fetch(`${base_backend_url}/eva/narration_improver/${currentUser.userID}/${currentUser.currentProject.projectID}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
    })
    .then(response => response.json())
    .then(data => {
      if (data.edits) {
        setNarrationImproverData(currentState => ({
            ...currentState,
            edits: data.edits
          }));
      }

      // Extract start and end times from edits and update scrubberTimestamps
      const newScrubberTimestamps = data.edits.reduce((acc, edit) => {
        // Add both start and end times for each edit
        acc.push(edit.start);
        acc.push(edit.end);
        return acc;
      }, []);

      setSources(sources => [...sources, ...new Array(newScrubberTimestamps.length/2).fill("NARRATION_IMPROVER")]);
    })
    .catch(error => {
      console.error('Error:', error);
    })
    .finally(() => {
      // disable button once the narration improver is ran
      setDisableBtn(true);
      setIsLoading(false); 
    });
    
  };

  const renderEdits = () => {
    if (isLoading) {
      return <div className='loading'></div>;
    }
    if (narrationImproverData.edits.length == 0) {
      return <p>Audio not cleaned yet or no transcribable audio is found.</p>;
    }
    let content;

      content = (
        <div id="feedback-section">
          <div>
          <ReactPlayer
              ref= {reactPlayerRef}
              controls
              onProgress = {skipAhead}
              onPlay = {playVideo}
              playing = {isPlaying}
              url={currentUser.currentProject.videoURL}
              width='100%'
              height='100%'
            />
          </div>
          <h3>Suggested Deleted Clips <Tooltip text="Displays all suggested to be removed clips. ↑ Send the deleted section to video streamliner tab"/></h3>

          <div className="narration-content">
            <ul id="edits_list">
              {narrationImproverData.edits && narrationImproverData.edits.map((edit, i) => (
                <li  key={i}>
                  <Original 
                    startingTimeInSeconds= {edit.start}
                    endingTimeInSeconds= {edit.end}
                    suggestedEdit={edit.label}
                    offset= {.5}
                    playVideo = {playVideo}
                    index={i}
                    setNarrationImproverData={setNarrationImproverData}
                  />
                </li>
              ))}
            </ul>
            
          </div>
        </div>
        
      );

    return content;
  };

  console.log("Sources:", sources)

  return (
    <div className="narration-improver"> 
        <h2>Narration Improver</h2>
        
        {!isLoading ? (
          <div className="content">
            {renderEdits()}
          </div>
        ): (
          //Loading Case
          <div className="content" style={{ alignItems: 'center', justifyContent: 'center' }}>
            {renderEdits()}
          </div>
        )
      }
       <button className="ni-generate-btn" disabled={disableBtn || !currentUser.currentProject.isUploaded || isLoading} title={!currentUser.currentProject.isUploaded ? "Video is uploading..." : ""} onClick={handleGenerate}>Suggest Narration Edits <Tooltip text="Provides narration edit suggestions"/></button>    </div>
  );
}

export default NarrationImprover;
