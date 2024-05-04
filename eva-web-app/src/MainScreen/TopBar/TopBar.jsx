import ProfileDropdown from "./Dropdowns/ProfileDropdown.jsx";
import BarButton from './BarButton.jsx'
import { useNavigate } from 'react-router-dom';
import techsmithlogo from '../../assets/techsmith_logo.png'
import './TopBar.css';

/* 
 * This CSS file styles the SidePanel component.
 *
 */
function TopBar({ setIsLoggedIn, onTabChange}) { 
    const navigate = useNavigate();

    function onHomeClicked() {
      navigate("/home");
    }
    const handleLogout = () => {
      setIsLoggedIn(false);
      navigate('/');
    };
    
    // Switch to selected tab
    const onStreamlinerClicked = () => {
      console.log("Streamliner Open!");
      onTabChange('streamliner'); 
    };

    const onNarratorClicked = () => {
      console.log("Narration Improver Open!");
      onTabChange('narrator'); 
    };

    const onFocusClicked = () => {
      console.log("Focus Group Open!");
      onTabChange('focus'); 
    };

    return (
      <div className="TopBar">
        <BarButton 
            text={<img 
                src={techsmithlogo}
                style={{aspectRatio: "1/1", height: "100%", borderRadius: "50%", border: "2px solid black"}}
            />} 
            divClass="button-div profile-button-div" 
            onButtonClicked={onHomeClicked}
            dropdownComponent={<ProfileDropdown logoutHandler={handleLogout}/>} 
              />
        <BarButton text="Video Streamliner" onButtonClicked={onStreamlinerClicked} />
        <BarButton text="Narration Improver" onButtonClicked={onNarratorClicked} />
        <BarButton text="Focus Group" onButtonClicked={onFocusClicked} />
      </div>
    )
  }


export default TopBar;
