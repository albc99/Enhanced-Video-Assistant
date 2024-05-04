import React, { useRef, useEffect, useContext } from 'react';
import './Project.css';

/**
 * VideoThumbnail is a functional component that creates and draws the thumbnail of a project video.
 *
 */

function VideoThumbnail({ videoUrl , buttonRef}) {
    const videoRef = useRef();
    const canvasRef = useRef();
    const imgRef = useRef();
    
    // This use effect is used to draw the thumbnail of the video and adjust the size of the thumbnail
    useEffect(() => {
        if (!buttonRef.current || !videoRef.current) return;

        const video = videoRef.current;
        video.onloadedmetadata = () => {
            const videoAspectRatio = video.videoWidth / video.videoHeight;
            const buttonRect = buttonRef.current.getBoundingClientRect();

            // For vertical videos, we need to adjust the thumbnail height
            if (videoAspectRatio < 1) {
                // The video is vertical
                imgRef.current.style.height = `${buttonRect.height}px`;
                imgRef.current.style.width = `${buttonRect.height * videoAspectRatio}px`;
            } else {
                // The video is horizontal
                imgRef.current.style.width = `${buttonRect.width}px`;
                imgRef.current.style.height = `${buttonRect.width / videoAspectRatio}px`;
            }
        };
        video.src = videoUrl;
    }, [videoUrl, buttonRef]);

    return (
        <div className="thumbnailContainer" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', width: '100%', height: '100%' }}>
            <img ref={imgRef} src={videoUrl} alt="thumbnail" className="thumbnail" style={{ objectFit: 'cover' }}/>
            <canvas ref={canvasRef} style={{ display: 'none' }}/>
        </div>
    );
}

export default VideoThumbnail;