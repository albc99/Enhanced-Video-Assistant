import React, { useEffect,useState,useContext } from 'react';
import Slider from '@mui/material/Slider';
import Stack from '@mui/material/Stack';
import IconButton from '@mui/material/IconButton';
import PlayArrowRoundedIcon from '@mui/icons-material/PlayArrowRounded';
import PauseIcon from '@mui/icons-material/Pause';
import VolumeDownRoundedIcon from '@mui/icons-material/VolumeDownRounded';
import { FeaturesDataContext } from '../../FeaturesDataContext.jsx';
import Box from '@mui/material/Box';
import './ManualControls.css';
import { scaleLinear } from 'd3-scale';
import { rgb } from 'd3-color';
import { interpolateRgb } from 'd3-interpolate';

const ManualControls = ({reactPlayerRef, reactPlayerSetIsPlaying, reactPlayerIsPlaying, duration, setVolume}) => {
    // const [isPlaying, setIsPlaying] = useState(false)
    const [audioSliderValue, setAudioSliderValue] = useState(30); // [0, 100]'    
    const [currentTime, setCurrentTime] = useState(0);
    const [isHovered, setIsHovered] = useState(false);
    const { focusGroupData,scrubberTimestamps } = useContext(FeaturesDataContext);
    const [greyedOutGradient, setGreyedOutGradient] = useState(null);


    const handleTimeSliderChange = (event, newValue) => {
        // Logic to handle slider value change
        reactPlayerRef.current.seekTo(newValue/100, "fraction");
    };

    const handleAudioChange = (event, newValue) => {
        setAudioSliderValue(newValue);
        setVolume(newValue/100);
      };

    const handlePlayPause = () => {
        if (reactPlayerIsPlaying) {
            reactPlayerSetIsPlaying(false);
        }
        else {
        reactPlayerSetIsPlaying(true);
        }
        // setIsPlaying(!isPlaying);
    };

    const formatTime = (time) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    };

    useEffect(() => {
        const interval = setInterval(() => {
          setCurrentTime(reactPlayerRef.current.getCurrentTime());
        }, 50);
      
        // Clear interval on component unmount
        return () => {
          clearInterval(interval);
        };
      }, [reactPlayerRef]);
    
      const chromaScales =  {
        "positive": scaleLinear().domain([0, 1]).range(["#FFFFFF", "#1FFF00"]).interpolate(interpolateRgb),
        "negative": scaleLinear().domain([0, 1]).range(["#FFFFFF", "#FF0000"]).interpolate(interpolateRgb),
        "neutral": scaleLinear().domain([0, 1]).range(["#FFFFFF", "#FFF700"]).interpolate(interpolateRgb)
    }


    function generateGreyedOutSegments() {
        if (scrubberTimestamps.length === 0) {
            return fullGradient;
        }
        if (colorStops === null) {
            return null;
        }
    
        // Flatten the colorStops array
        let flatColorStops = colorStops.flat();
    
        let greyedOutColorStops = [];
    
        scrubberTimestamps.forEach((timestamp, index) => {
            const startPercentage = (timestamp / duration) * 100;
            const endPercentage = ((index < scrubberTimestamps.length - 1 ? scrubberTimestamps[index + 1] : duration) / duration) * 100;
    
            flatColorStops.forEach(colorStop => {
                const [colorStart, colorEnd] = colorStop.split(', ');
                const [color, colorStartPercentage] = colorStart.split(' ');
                const colorEndPercentage = colorEnd.split(' ')[1];
    
                // Check if the color stop falls within the greyed out segment
                if (startPercentage <= parseFloat(colorEndPercentage) && parseFloat(colorStartPercentage) <= endPercentage) {
                    // Split the color stop into two if necessary
                    if (startPercentage > parseFloat(colorStartPercentage)) {
                        greyedOutColorStops.push(`${color} ${colorStartPercentage}, ${color} ${startPercentage}`);
                    }
                    if (endPercentage < parseFloat(colorEndPercentage)) {
                        greyedOutColorStops.push(`${color} ${endPercentage}, ${color} ${colorEndPercentage}`);
                    }
    
                    // Replace the color with grey
                    greyedOutColorStops.push(`#9EA2A3 ${Math.max(startPercentage, parseFloat(colorStartPercentage))}, #9EA2A3 ${Math.min(endPercentage, parseFloat(colorEndPercentage))}`);
                } else {
                    greyedOutColorStops.push(colorStop);
                }
            });
        });
    
        return `linear-gradient(to right, ${greyedOutColorStops.join(', ')})`;
    }

    function generateGradient() {
        var timestampsAndColors = [];
    
        if (focusGroupData == null) {
            return null;
        }
    
        let colorStops = null;
    
        if (focusGroupData.clip_tones && focusGroupData.clip_tones.length > 0) {
            timestampsAndColors = focusGroupData.clip_tones.map((segment, index) => {
                const colorScale = chromaScales[segment.sentiment_label];
                const color =  colorScale(segment.sentiment_score);
                const colorHex = rgb(color).formatHex();
                return [[segment.start, segment.end], colorHex];
            });
    
            colorStops = timestampsAndColors.map(([timestamps, color]) => {
                const startPercentage = (timestamps[0] / duration) * 100;
                const endPercentage = (timestamps[1] / duration) * 100;
                return `${color} ${startPercentage}%, ${color} ${endPercentage}%`;
            });
        }
    
        return {
            fullGradient: colorStops ? `linear-gradient(to right, ${colorStops.join(', ')})` : null,
            colorStops: colorStops
        };
    }
    
    const { fullGradient, colorStops } = generateGradient();

    return (
        <div className='video-controls-container'>
            <div className='time-slider-container'>
                <Slider
                    sx={{"& .MuiSlider-rail": {background:fullGradient,height:"45%"},"& .MuiSlider-track":{background:"transparent",border:"none"}}}
                    min={0}
                    max={100}
                    value = {currentTime/duration*100}
                    onChange={handleTimeSliderChange}
                    className="time-slider"
                />
            </div>
            <div className='video-controls-row2-container'>
                <div className='play-pause-audio-container'>
                    <IconButton aria-label="play" size="large" color="primary" onClick={handlePlayPause}>
                        {reactPlayerIsPlaying ? <PauseIcon fontSize="inherit"/> : <PlayArrowRoundedIcon  fontSize="inherit"/>}
                    </IconButton>
                    <div className='video-timestamp'>
                        {formatTime(currentTime)} / {formatTime(duration)}
                    </div>
                    <Box 
                        className="audio-slider-box"
                        onMouseEnter={() => setIsHovered(true)}
                        onMouseLeave={() => setIsHovered(false)}
                        >
                        <Stack spacing={0.4} direction="row">
                            <VolumeDownRoundedIcon />
                            {isHovered && (
                            <Slider className="audio-slider" value={audioSliderValue} onChange={handleAudioChange} />
                            )}
                        </Stack>
                    </Box>
                    
                    
                </div>

            </div>
        </div>
    );
};

export default ManualControls;


;
