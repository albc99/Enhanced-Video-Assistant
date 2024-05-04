
import Slider from '@mui/material/Slider'
import ReactSlider from "../../../components/ReactSlider.jsx"
import './CuttingScrubber.css'
import React, { useEffect, useState, useContext } from 'react'
import { FiZoomIn, FiZoomOut } from 'react-icons/fi';
import Tooltip from '@mui/material/Tooltip';
import { FeaturesDataContext } from '../../../FeaturesDataContext.jsx';


function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

function CuttingScrubber({ reactPlayerRef, duration }) {
    const [zoomRange, setZoomRange] = useState([0, duration]);
    const [zoomLevel, setZoomLevel] = useState(100);
    const [isRestoring, setIsRestoring] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [testState, setTestState] = useState(true)
    const [zoomValue, setZoomValue] = useState(0)
    const { streamlinerData, scrubberTimestamps, setScrubberTimestamps,setCurrentSelectedOptionsTimestamps } = useContext(FeaturesDataContext);

    const visibleStart = zoomValue / 100 * duration;
    const visibleEnd = visibleStart + (1 - zoomValue / 100) * duration; 

    //tracking visibility for thumbs
    const [thumbHover, setThumbHover] = useState(new Array(scrubberTimestamps.length).fill(false));

    const calculateZoomFactor = () => {
      const currentZoomWidth = zoomRange[1] - zoomRange[0];
      return Math.max(0.05, 0.1 * (currentZoomWidth / duration));
    };

    const handleZoomIn = () => {
      setZoomValue(prevZoomValue => Math.min(100, prevZoomValue + 10));
    };
    
    const handleZoomOut = () => {
      setZoomValue(prevZoomValue => Math.max(0, prevZoomValue - 10));
    };

    const sliderContainerStyle = {
      overflowX: 'auto', 
      width: '100%', 
    };
    const sliderStyle = {
      width: `${(zoomRange[1] - zoomRange[0]) / duration * 100}%`, 
      minWidth: '100%', 
    };
    const sliderWidth = `${Math.max(100, ((zoomRange[1] - zoomRange[0]) / duration) * 100)}%`;

  
    const handleThumbHover = (index, hover) => {
      setThumbHover((prev) => prev.map((v, i) => (i === index ? hover : v)));
  };

    // const [duration, setDuration] = useState(0);

    const handleChange = (newValue, thumbIndex) => {
      // console.log("Timestamps:", timestamps, " NewValue:", newValue)
      // console.log(newValue)
      setScrubberTimestamps(newValue);
      // reactPlayerRef.current.seekTo(newValue.at(newValue.length - 1) / duration, 'fraction');
    };

    useEffect(() => {
      const initialTimestamps = streamlinerData.deleted_clip_timestamps.flat();
      if (initialTimestamps[initialTimestamps.length - 1] === "end") {
        initialTimestamps[initialTimestamps.length - 1] = duration
      }
      console.log("New timestamps from scrubber:", initialTimestamps)
      setScrubberTimestamps(initialTimestamps);
      // setCurrentSelectedOptionsTimestamps(initialTimestamps);
  }, [streamlinerData.deleted_clip_timestamps, duration])

    useEffect(() => {
      setCurrentSelectedOptionsTimestamps(scrubberTimestamps)
    }, [scrubberTimestamps])
  
    function addDeletedClip(event) {
      // console.log("Current timestamps:", scrubberTimestamps)
      if (!isDeleting && isRestoring) {
        return
      }

      setIsDeleting(!isDeleting)
      // setTimestamps([10, 20])
    }

    function activateRemoveMode() {
      if (!isRestoring && isDeleting) {
        return
      }

      setIsRestoring(!isRestoring)
    }

    const marks = [
      {
        value: 0,
        label: '00:00',
      },
      {
        value: duration,
        label: formatDuration(duration),
      },
    ];

    const renderThumb = (props, { index }) => { 
      if (scrubberTimestamps.length < 1) {
        return <div {...props} className=''></div>
      }

      // console.log(`Thumb ${index}, Timestamp in seconds:`, timestamps[index]);
  
      let tooltipTitle = 'Loading...';
      if (typeof scrubberTimestamps[index] === 'number' && !isNaN(scrubberTimestamps[index])) {
          const formattedTimestamp = formatDuration(scrubberTimestamps[index]);
          tooltipTitle = formattedTimestamp;
      }
      // console.log(`Thumb ${index}, Tooltip title:`, tooltipTitle);
  
      return (
          <Tooltip
              title={tooltipTitle}
              open={thumbHover[index]}
              enterTouchDelay={0}
              leaveTouchDelay={0}
              placement="top"
          >
              <div
                  {...props}
                  onMouseEnter={() => handleThumbHover(index, true)}
                  onMouseLeave={() => handleThumbHover(index, false)}
              />
          </Tooltip>
          // <div {...props}></div>
      );
  };
  
  
  

    const renderTrack = (props, state) => {
      // console.log("Rendering track:", state.index)

      if (isDeleting) {
        let className = `${props.className} glowing`

        if (scrubberTimestamps.length < 1) {
          return <div {...props} className={className}></div>
        }

        if (state.index % 2 === 1) {
          className = `${props.className} odd-track glowing`
        }
        return <div {...props} className={className}></div>
      }


      if (scrubberTimestamps.length < 1) {
        return <div {...props}></div>
      }

      if (state.index % 2 === 1) {
        let className = `${props.className} odd-track`

        if (isRestoring) {
          className = `${props.className} odd-track glowing`
        }

        return <div {...props} className={className}></div>
      }
      else {
        return <div {...props}></div>
      }
    }

    function onSliderClick(value) {
      console.log("Clicked with value:", value)

      if (isDeleting) {
        let timestamps = [value - 0.5, value + 0.5]

        console.log("Adding timestamps from", timestamps[0], "to", timestamps[1])
        
        setScrubberTimestamps((currentValues) => {
          let newArray = [...currentValues, timestamps[0], timestamps[1]]
          console.log("Unsorted", newArray)
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

        setIsDeleting(currentVal => false)
      }

      if (scrubberTimestamps.length < 1) {
        return
      }

      if (isRestoring) { 
        let upperBoundIndex = 0

        while (upperBoundIndex < scrubberTimestamps.length && value > scrubberTimestamps[upperBoundIndex]) {
          upperBoundIndex += 1
        }
  
        if (upperBoundIndex >= scrubberTimestamps.length) {
          return
        }
  
        if (upperBoundIndex % 2 == 1) {
          console.log("Want to remove deleted zone between", scrubberTimestamps[upperBoundIndex - 1], "and", scrubberTimestamps[upperBoundIndex])
          
          console.log(scrubberTimestamps)
          let tempArray = []
          for (let i = 0; i < scrubberTimestamps.length; i++) {
            if (i !== upperBoundIndex && i !== upperBoundIndex - 1) {
              tempArray.push(scrubberTimestamps[i])
            }
          }
          console.log(tempArray)
  
          setScrubberTimestamps(tempArray)
          // setTimestamps([])
        }
      }
    }
  
    return (
      <div className="customScrubber">
        <div className="add-btn-container">
          <button className="addButton addDeleteZone" onClick={addDeletedClip}>{isDeleting ? "Cancel Deletion" : "Add Deleted Zone"}</button>
          <button className="addButton addDeleteZone" onClick={activateRemoveMode}>{isRestoring ? "Deactivate Restore Mode" : "Activate Restore Mode"}</button>
        </div>
        {/* <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', marginBottom: '10px' }}>
          <div>{formatDuration(zoomRange[0])}</div> 
          <div>{formatDuration(zoomRange[1])}</div> 
        </div> */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div style={{ fontSize: '0.8em', color: '#888', transition: 'all 0.3s ease-in-out', padding: '5px', borderRadius: '5px', backgroundColor: '#393844' }}>
            {formatDuration(visibleStart)} 
          </div>
          <div className="scrubberContainer">
            <div style={{width: `${100 + 3 * zoomValue}%`, height: "100%"}}>
              {/* {console.log("Div width:", 100 + 3 * zoomValue)} */}
              <ReactSlider
                className="horizontal-slider"
                thumbClassName="slider-thumb"
                trackClassName="slider-track"
                snapDragDisabled={true}
                defaultValue={[]}
                value={scrubberTimestamps}
                onChange={handleChange}
                renderTrack={renderTrack}
                renderThumb={renderThumb}
                onSliderClick={onSliderClick}
                disabled={isRestoring || isDeleting}
                min={0}
                max={duration}
                step={duration / 1000000}
                pearling
                minDistance={0}
                withTracks={true}
              />
            </div>
          </div>
          <div style={{ fontSize: '0.8em', color: '#888', transition: 'all 0.3s ease-in-out', padding: '5px', borderRadius: '5px', backgroundColor: '#393844' }}>
            {formatDuration(visibleEnd)} 
          </div>
        </div>
        <div className="zoomSliderContainer">
          {/* <span className="zoomLabel">Zoom level:</span> */}
          <button className="zoomButton zoomOut" onClick={handleZoomOut}><FiZoomOut /></button>
          <Slider
            className="zoomSlider"
            value={zoomValue}
            onChange={(event, newValue) => {
              // console.log("New slider zoom val", newValue)
              setZoomValue(newValue)
            }}
            aria-labelledby="zoom-level-slider"
            valueLabelDisplay="auto"
            valueLabelFormat={(value) => `${value.toFixed(0)}%`}
            min={0}
            max={100}
          />
          
          <button className="zoomButton zoomIn" onClick={handleZoomIn}><FiZoomIn /></button>
        </div>
          
      </div>
    );
    
    
}

export default CuttingScrubber