import { useContext } from 'react';
import { CurrentUserContext } from '../../../CurrentUserContext.jsx';
import { FeaturesDataContext } from '../../../FeaturesDataContext.jsx';
import './VideoStreamliner.css'

/**
 * DeletedClip is a functional component that represents a deleted clip in the video streamliner tab.
 *
 */

function convertNumTo2Places(num) {
  return num < 10 ? '0' + num : num;
}

function DeletedClip({ startingTimeInSeconds, endingTimeInSeconds, playVideo, timestampIndex }) {
  const { currentUser } = useContext(CurrentUserContext);
  const { scrubberTimestamps, setScrubberTimestamps } = useContext(FeaturesDataContext)

  const restoreTimestamps = e => {
    e.stopPropagation()
    let newArray = []

    for (let i = 0; i < scrubberTimestamps.length; i++) {
      if (i !== timestampIndex && i !== timestampIndex + 1) {
        newArray.push(scrubberTimestamps[i])
      }
    }

    setScrubberTimestamps(newArray)
  }
  return (
      <div className="timestamp-restore-btns">
        <button className="play-btn" title="Add timestamp to timeline" style={{maxHeight:"15vh", cursor: "pointer"}} onClick={() => playVideo(startingTimeInSeconds, endingTimeInSeconds)}>
            {"▶⠀"}
                {convertNumTo2Places(Math.floor((startingTimeInSeconds.toFixed(2))/ 60))}:
                {convertNumTo2Places(Math.round(((startingTimeInSeconds.toFixed(2))% 60)*1e12)/1e12)} -{' '}
                {convertNumTo2Places(Math.floor((endingTimeInSeconds.toFixed(2))/ 60))}:
                {convertNumTo2Places(Math.round(((endingTimeInSeconds.toFixed(2))% 60)*1e12)/1e12)}
                </button>
        <button className="restore-btn" title="Add timestamp to timeline" onClick={restoreTimestamps} style={{maxHeight:"15vh", backgroundColor: "#205180"}}>
           {"↩"}
        </button>
      </div>
  );
}

export default DeletedClip;