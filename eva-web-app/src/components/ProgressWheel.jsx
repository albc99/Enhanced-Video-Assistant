import React, { useEffect, useState, useRef } from 'react';
import './ProgressWheel.css';

function ProgressWheel ({durationInSeconds}) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const startTime = Date.now();
    const endTime = startTime + durationInSeconds * 1000;
    var currentPercent = 0;
    var timeSave = 0;
    var compare_num = 1.2;
    function updateProgress (){
        const elapsedTime = Date.now() - startTime;
        if(currentPercent < 99){
          currentPercent = (elapsedTime / (endTime - startTime)) * 100
          setProgress(currentPercent)
          timeSave = Date.now() - startTime
        }
        else{
          if(currentPercent < 99.8){
          //Exponentially increases the 99.1... Making so that progress can still increase no matter what
            if(elapsedTime/timeSave >= compare_num){
              compare_num = compare_num * 1.06
              currentPercent = currentPercent + 0.1
              setProgress(currentPercent)
              timeSave = elapsedTime
            }
          }
        }

    };

    //Call this function every 50ms
    const interval = setInterval(updateProgress, 50);
    
    return () => clearInterval(interval);
}, [durationInSeconds]);

function fillBar(){
  return {width:`${progress}%`}
}

  return (
    <div id='progress-bar-container'>
      <div id="progress-bar">
        <div id="progress-bar-fill" style={fillBar()}></div>
      </div>
      <h1>{progress >= 99 ? progress.toFixed(1) : progress.toFixed(0)}%</h1>
    </div>
  );
};

export default ProgressWheel;
