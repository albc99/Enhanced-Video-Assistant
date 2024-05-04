import React from 'react';
import './tooltip.css'; 

function MyComponent({text}) {
  return (
    <div class="tooltip"> {"ⓘ"}
        <span class="tooltiptext">{text}</span>
    </div>
  );
}

export default MyComponent;