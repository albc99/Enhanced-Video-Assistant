import { useContext, useState,useRef, useEffect } from 'react'
import ReactPlayer from 'react-player'
import CuttingScrubber from './CuttingScrubber/CuttingScrubber.jsx';
import { CurrentUserContext } from '../../CurrentUserContext.jsx';
import TimestampedVideoPlayer  from './TimestampedVideoPlayer.jsx';
import './VideoViewport.css';
import base_backend_url from '../../base_backend_url.js';
import ManualControls from './ManualControls.jsx';
import Modal from 'react-modal';
import LoadingWheel from '../../components/LoginLoadingWheel.jsx';
import { FeaturesDataContext } from '../../FeaturesDataContext.jsx';
import DownloadIcon from '@mui/icons-material/Download';
import HelpButton from './HelpButton.jsx';
import Tooltip from '../../components/tooltip.jsx'
/**
 * VideoViewport is a functional component that handles the video viewport in the application.
 *
 */
function VideoViewport({url, activeTab}) 
{
    const {currentUser, setCurrentUser} = useContext(CurrentUserContext)
    const [videoFile, setVideoFile] = useState(null);
    const [duration, setDuration] = useState(0);
    const [currentOutputVideoUrl, setcurrentOutputVideoUrl] = useState(null);
    const [currentOriginalVideoUrl, setCurrentOriginalVideoUrl] = useState(url)
    const [isPlaying, setIsPlaying] = useState(false);
    const [volume, setVolume] = useState(0.6);
    const { currentSelectedOptionsTimestamps,scrubberTimestamps, setIsLoadingFeatureData, isLoadingFeatureData} = useContext(FeaturesDataContext);
    const [normalizeAudio, setNormalizeAudio] = useState(true);
    const reactPlayerRef = useRef(null);
    const timestampUpperBoundIndex = useRef(0)
    const [blobUrl, setBlobUrl] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isButtonDisabled, setIsButtonDisabled] = useState(true);
    const [modalIsOpen, setIsOpen] = useState(false);

    // Download the video locally
    const handleDownloadVideo = () => {
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = 'processed_video.mp4';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    useEffect(() => {
        setIsButtonDisabled(false);
    }, [scrubberTimestamps])
    
    const timestampList = [];
    const getFileURL = (fileObject) => {
        
        if (fileObject) {
            console.log("Making video url for non null file")
            console.log((URL.createObjectURL(fileObject)))
            console.log(fileObject)
            return URL.createObjectURL(fileObject)
        }
    
        return ''
    }


    useEffect(() => {
        if(currentUser.currentProject.videoFile != null){
            console.log("file")
            setCurrentOriginalVideoUrl(getFileURL(currentUser.currentProject.videoFile))
        }
        else if (currentUser.currentProject.originalVideoFileUrl != null){
            setCurrentOriginalVideoUrl(currentUser.currentProject.originalVideoFileUrl) //streaming
        }
        else {
            console.warn("No video will display );")
        }
    }, [currentUser.currentProject.videoFileUrl, 
        currentUser.currentProject.originalVideoFileUrl])

    const setReactPlayerRef = (playerRef) => {
        reactPlayerRef.current = playerRef;
      };


    function getUpperBoundIndex(playedSeconds) {
        let currentIndex = 0;
        while (playedSeconds >= currentSelectedOptionsTimestamps[currentIndex] && currentIndex < currentSelectedOptionsTimestamps.length) {
            currentIndex += 1;
        }

        if (currentIndex == currentSelectedOptionsTimestamps.length) {
            return currentSelectedOptionsTimestamps.length
        }

        return currentIndex
    }
    

    function onProgress({played, loaded, playedSeconds, loadedSeconds}) {
        if (currentSelectedOptionsTimestamps.length < 1) {
            return
        }
        
        let correctUpperBoundIndex = getUpperBoundIndex(playedSeconds)

        if (correctUpperBoundIndex % 2 == 1) {
            reactPlayerRef.current.seekTo(currentSelectedOptionsTimestamps[correctUpperBoundIndex])
            timestampUpperBoundIndex.current = correctUpperBoundIndex + 1
        }
        else {
            timestampUpperBoundIndex.current = correctUpperBoundIndex
        }

        if (timestampUpperBoundIndex.current >= currentSelectedOptionsTimestamps.length) {
            return
        }

        if (playedSeconds >= currentSelectedOptionsTimestamps[timestampUpperBoundIndex.current]) {
            timestampUpperBoundIndex.current += 1

            // even indices start deleted clips,
            // odd indices end deleted clips
            if (timestampUpperBoundIndex.current % 2 == 1) {
                let secondsToSeekTo = currentSelectedOptionsTimestamps[timestampUpperBoundIndex.current]
                reactPlayerRef.current.seekTo(secondsToSeekTo)
            }
        }
    }
    
    function applyAndGenerate() {
        setIsButtonDisabled(true);
        console.log("Apply and generate clicked");
        setIsOpen(true);
        setIsLoading(true)
        let correctedTimestamps = [0]
        scrubberTimestamps.forEach(element => {
            if (element === 'end') {
                element = reactPlayerRef.current.getDuration();
            }
            correctedTimestamps.push(element)
        });
       
        correctedTimestamps.push(duration)

        console.log("Corrected timestamp list:", correctedTimestamps)
        fetch(`${base_backend_url}/eva/generate_video/${currentUser.userID}/${currentUser.currentProject.projectID}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
              },
            body: JSON.stringify({"scrubber_timestamps":correctedTimestamps,"normalize_audio":normalizeAudio}),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to generate video');
            }
            return response.json();
        })
        .then(data => {
            const filePath = data.outputFilePath;
            const name = currentUser.currentProject.projectID + '.mp4'
            const destinationUrl = `${base_backend_url}/azure_blob/get_current_video/?videoname=processed_${encodeURIComponent(name)}`;

            fetch(destinationUrl,{
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                  },
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to retrieve video');
                    }
                    return response.blob();
                })
                .then(blob => {
                    const blobUrl = URL.createObjectURL(blob);
                    console.log("Created blob URL:", blobUrl);

                    setcurrentOutputVideoUrl(blobUrl);
                    setBlobUrl(blobUrl);
                    setIsLoading(false);
                    setIsOpen(false);

                })
                .catch(error => {
                    console.error('Error:', error);
                    // Handle error here, e.g., show an error message to the user
                });
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        // Handle error here, e.g., show an error message to the user
                    });   
                }

    const [isOriginalVideo, setIsOriginalVideo] = useState(true);

    const handleToggleVideo = () => {
        setIsOriginalVideo(!isOriginalVideo);
        

    };  
    return (  
        <div className="video-viewport-container">
            <Modal
                    ariaHideApp={false}
                    overlayClassName="grey-out-overlay"
                    className="select-options-popup-content"
                    isOpen={modalIsOpen}
                    >
                        {(
                        <div>
                            <LoadingWheel text="Generating New Video"/>
                        </div>)}
                    </Modal>
            <div className="video-viewport">
                {isOriginalVideo || !currentOutputVideoUrl ? (
                    <div style={{width:"100%" , height:"100%"}}>
                        <ReactPlayer
                            ref={(player) => setReactPlayerRef(player)}
                            url={currentOriginalVideoUrl}
                            playing={isPlaying}
                            width="100%"
                            height={"80%"}
                            volume={volume}
                            onProgress={onProgress}
                            progressInterval={1}
                            onDuration={duration => setDuration(duration)}
                            onEnded={() => setIsPlaying(false)}
                        />
                        
                        <ManualControls 
                            reactPlayerRef={reactPlayerRef} 
                            duration={duration}
                            reactPlayerSetIsPlaying={setIsPlaying}
                            reactPlayerIsPlaying={isPlaying}
                            setVolume={setVolume} 
                        />

                    </div>
                    
                ) : (
                    <div className='outputvideocontainer'>
                    <ReactPlayer
                        url={currentOutputVideoUrl}
                        controls
                        width="100%"
                        height={"80%"}
                        />
                        {currentOutputVideoUrl && !isOriginalVideo && (<button className="download-buttonasd" onClick={handleDownloadVideo}>Download<DownloadIcon /></button>)}
                    </div>
                    
                )}
                {currentOutputVideoUrl && !isOriginalVideo && <button className="left-arrow-btn" onClick={handleToggleVideo}>←</button>}
                {currentOutputVideoUrl && isOriginalVideo && <button className="right-arrow-btn" onClick={handleToggleVideo}>→</button>}
            </div>
        

        <div className='special-button-container'>
            {/* <TimestampedVideoPlayer/> */}
            <HelpButton className="help-button"></HelpButton>
            <div>
                
            <label htmlFor="myCheckbox" style={{fontSize:"1.2vw"}}>Normalize audio </label>

            <input type="checkbox" id="myCheckbox" style={{width:"2vh",height:"2vh"}} checked={normalizeAudio} onChange={() => setNormalizeAudio(!normalizeAudio)}/> 
                <button className="generate-video-btn" role="button" onClick={applyAndGenerate}>Render & Export<Tooltip text="Generates a new video based on current timeline"/></button>

            </div>
        </div>

        <CuttingScrubber 
            reactPlayerRef={reactPlayerRef} 
            duration={duration}
        />
       
    </div>
)
}

export default VideoViewport;