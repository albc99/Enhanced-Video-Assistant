import React, { useEffect, useContext } from "react";
import './FocusGroupBar.css';
import { FeaturesDataContext } from '../../FeaturesDataContext.jsx';
import chroma from 'chroma-js';

function FocusGroupBar({ reactPlayerRef, duration }) {
    const { focusGroupData } = useContext(FeaturesDataContext);

    const chromaScales = {
        "positive": chroma.scale(colors=["#90ee90", "green"]), // light green to strong green
        "negative": chroma.scale=(["#ffcccb", "red"]), // light red to strong red
        "neutral": chroma.scale=(["#d3d3d3", "gray"]) // light gray to strong gray
    }

    const handleClick = (segment) => {
        console.log(`Navigating to time ${segment.start} in the video`);
        reactPlayerRef.current.seekTo(segment.start, 'seconds');
    }

    return (
        <div className="focusgroup-bar">
            {focusGroupData.clip_tones && focusGroupData.clip_tones.map((segment, index) => {
                const colorScale = chromaScales[segment.sentiment_label];
                const color = colorScale(segment.sentiment_score).hex();
                return (
                    <div
                        key={index}
                        style={{ width: `${(segment.end - segment.start) / duration * 100}%`, backgroundColor: color }}
                        onClick={() => handleClick(segment)}>
                    </div>
                );
            })}
        </div>
    )
}

export default FocusGroupBar;