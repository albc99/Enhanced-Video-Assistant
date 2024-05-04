import './SidePanel.css'

/**
 * SidePanel is a functional component that serves as a container for other components.
 *
 */
function SidePanel({children})
{
    return (
        <div className="sidepanel">
            {children}
        </div>
    )
}

export default SidePanel;
