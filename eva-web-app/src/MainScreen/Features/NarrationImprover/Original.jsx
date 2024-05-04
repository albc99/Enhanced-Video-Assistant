import { useContext, useRef, useState } from 'react';
import { FeaturesDataContext } from '../../../FeaturesDataContext.jsx';
import './NarrationImprover.css';

function convertNumTo2Places(num) {
    return num < 10 ? '0' + num : num;
}

function Original({ startingTimeInSeconds, endingTimeInSeconds, offset, suggestedEdit, playVideo, index, setNarrationImproverData }) {    const reactPlayerRef = useRef(null);
    const { setScrubberTimestamps } = useContext(FeaturesDataContext)

    const sendToDeletedClips = () => {

      setNarrationImproverData(currentData => {
        let newEdits = []


        for (let i = 0; i < currentData.edits.length; i++) {
          if (i !== index) {
            newEdits.push(currentData.edits[i])
          }
        }


        return {
          ...currentData,
          edits: newEdits
        }
      })

      setScrubberTimestamps(currentTimestamps => {
        let newArray = [...currentTimestamps, startingTimeInSeconds, endingTimeInSeconds]
        newArray = newArray.sort((a, b) => {
          if (a < b) {
            return -1
          }
          else {
            return 1
          }
        })
        console.log("New array", newArray)
        return newArray
      })
    }
    return (
      <div className="timestamp-restore-btns" >
      <button className ="play-btn" title="Play suggested clip to be deleted" onClick={() => playVideo(startingTimeInSeconds - offset, endingTimeInSeconds+offset, offset)} style={{maxHeight:"5vh", backgroundColor:"#cfb456"}}>
      {"▶⠀"}
      {suggestedEdit + " "}
      {convertNumTo2Places(Math.floor((startingTimeInSeconds -offset)/ 60))}:
          {convertNumTo2Places(Math.round(((startingTimeInSeconds -offset)% 60)*1e12)/1e12)} -{' '}
          {convertNumTo2Places(Math.floor((endingTimeInSeconds +offset)/ 60))}:
          {convertNumTo2Places(Math.round(((endingTimeInSeconds +offset)% 60)*1e12)/1e12)}
        </button>
        <button onClick={sendToDeletedClips} className="restore-btn" title="Send clip to deleted clips" style={{maxHeight:"5vh", backgroundColor: "#205180"}}>
       {"↑"}     
    </button>
    </div>
    );
  }
  
  export default Original;
