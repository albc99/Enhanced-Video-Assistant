
function BarButton({text, dropdownComponent, divClass, buttonClass, onButtonClicked})
{
    return (
        <div className={divClass == null ? "button-div" : divClass}>
            <button 
                className={buttonClass == null ? "bar-button" : buttonClass}
                type="button"
                onClick={onButtonClicked}
            >
                {text}
            </button>
            {dropdownComponent}
        </div>
    )
}

export default BarButton;