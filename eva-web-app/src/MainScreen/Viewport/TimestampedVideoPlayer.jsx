import React, { useContext, useState, useRef } from 'react';
import './TimestampedVideoPlayer.css';
import Select from 'react-select';
import Modal from 'react-modal';
import { FeaturesDataContext } from '../../FeaturesDataContext.jsx';

function TimestampedVideoPlayer() {

  const [selectedOptions, setSelectedOptions] = useState(['Key Moments']);
  const [savedOptions, setSavedOptions] = useState([]);
  
  const [selectedSection, setSelectedSection] = useState("Key Moments");
  const [modalIsOpen, setIsOpen] = useState(false);
  const { streamlinerData,narrationImproverData,focusGroupData,scrubberTimestamps,setCurrentSelectedOptionsTimestamps } = useContext(FeaturesDataContext);
  const sections = ["Key Moments", "Full Video"]
  const options =  ['Postive', 'Negative', 'Neutral','Bad audio']

  const handlePlayButtonClick = () => {
    setIsOpen(true);
  };

  const closeModal = () => {
    setIsOpen(false);
  };
  const handleSectionChange = (section) => {
    setSelectedSection(section);
  };

  const handleCheckboxChange = (option) => {
    setSelectedOptions(prevSelectedOptions => {
      if (prevSelectedOptions.includes(option)) {
        return prevSelectedOptions.filter(o => o !== option);
      } else {
        return [...prevSelectedOptions, option];
      }
    });
  };

  const getBadAudioTimestamps = () =>{
    var badAudioTimestamps = []
    for (let edit of narrationImproverData.edits){
      badAudioTimestamps.push(edit.start);
      badAudioTimestamps.push(edit.end);
    }
    return badAudioTimestamps;
  }
  const getToneTimestamps = () =>{  
    console.log("getting tone timestamps")
    var toneTimestamps = []
    for (let segment of focusGroupData.clip_tones){
      if (selectedOptions.map(option => option.toLowerCase()).includes(segment.sentiment_label.toLowerCase())){
        toneTimestamps.push(segment.start);
        toneTimestamps.push(segment.end);
      }
    }
    console.log(toneTimestamps);
    return toneTimestamps;
  }
    function mergeTimestamps(timestamps1, timestamps2) {
      let result = [];

      for (let i = 0; i < timestamps2.length; i += 2) {
          let addStart = timestamps2[i];
          let addEnd = timestamps2[i + 1];

          for (let j = 0; j < timestamps1.length; j += 2) {
              let tsStart = timestamps1[j];
              let tsEnd = timestamps1[j + 1];

              // If the current start is less than or equal to the last end, there's an overlap
              if (tsStart <= addEnd && tsEnd >= addStart) {
                  // Add the overlapping segment to the result
                  if (Math.max(tsStart, addStart)!== Math.min(tsEnd, addEnd)){
                    result.push(Math.max(tsStart, addStart), Math.min(tsEnd, addEnd));
                  }
              }
          }
      }

      return result;
  }

  const handleSave = () => {
    // check if options changed
    const newOptions = selectedOptions.filter(option => !savedOptions.includes(option));

    console.log("newoptions",newOptions);
    console.log("timestamps",scrubberTimestamps);
    console.log("selectedSection",selectedSection);
    console.log("aaaasey",selectedSection == "Key Moments");
    
    console.log("aaafull",selectedSection == "Full Video");
    console.log("selectd options",selectedOptions);
    console.log("saved options",savedOptions);
    console.log("badaudiotimestamps",getBadAudioTimestamps());
    console.log("tonetimestamps",getToneTimestamps());
    // add nad merge selected options timestamps while checking for overlapping timestamps
    if (newOptions.length > 0){
      var timestamps = [];
      if (selectedSection == "Key Moments"){
        timestamps = scrubberTimestamps;
      } 
      if (newOptions.includes('Bad audio')){
        if (timestamps.length > 0){
          timestamps = mergeTimestamps(timestamps, getBadAudioTimestamps());
        }
        else{
          timestamps = getBadAudioTimestamps();
        }
      }
      if (newOptions.includes('Positive') || newOptions.includes('Negative') || newOptions.includes('Neutral')){
        if (timestamps.length > 0){
          timestamps = mergeTimestamps(timestamps, getToneTimestamps());
        }
        else{
          timestamps = getToneTimestamps();
        }
      }
      
    console.log("setCurrentSelectedOptionsTimestampstimestamps",timestamps);
    setCurrentSelectedOptionsTimestamps(timestamps);
    setSavedOptions(selectedOptions);
    }
    console.log("setCurrentSelectedOptionsTimestampstimestamps",timestamps);
    closeModal();
  };


  return (
    <div style={{display:"flex",flexDirection:"row"}}>
      <button className='select-options-button' onClick={handlePlayButtonClick}>More play options &#9660;</button>
      <Modal
        ariaHideApp={false}
        overlayClassName="select-options-popup-overlay"
        className="select-options-popup-content"
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
      >
        <div style={{display:"flex", flexDirection:"row",justifyContent:"space-between"}}>
          <h2>Play options</h2>
          <button onClick={closeModal}>X</button>
        </div>
        <div className="sections-container">
        {sections.map(section => (
    <button
      key={section}
      className={`section-button ${selectedSection === section ? 'selected' : ''}`}
      onClick={() => handleSectionChange(section)}
    >
      {section}
    </button>
  ))}
        </div>
            <h3 style={{fontSize:"1.5vw"}}>Play selected version with specific tags</h3>
          <div className="select-options-container">
            {options.map(option => (
              <div
                className={`select-option-btn ${selectedOptions.includes(option) ? 'selected' : ''}`}
                key={option}
                onClick={() => handleCheckboxChange(option)}
              >
                {option}
              </div>
            ))}
          </div>
        <button className="selected-options-save-btn"onClick={handleSave}>Save</button>
        
      </Modal>
    </div>
  );
}

export default TimestampedVideoPlayer;


