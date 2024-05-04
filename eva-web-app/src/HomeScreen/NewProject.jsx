import React from 'react';
import { useState, useContext } from 'react';
import newprojecticon from './newfoldericon.png';
import { useNavigate } from 'react-router-dom';
import { CurrentUserContext } from '../CurrentUserContext';
import './Project.css';
import './NewProject.css';
import base_backend_url from '../base_backend_url';
import Modal from 'react-modal';
import { IconButton } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ProgressWheel from '../components/ProgressWheel.jsx';
import Tooltip from '../components/tooltip.jsx'
import Select from 'react-select';

/**
 * NewProject is a functional component that allows the user to create a new project.
 *
 */
function NewProject() {
    const [showPopup, setShowPopup] = useState(false);
    const navigate = useNavigate(); 
    const {currentUser, setCurrentUser} = useContext(CurrentUserContext)
    const [isCompressing, setIsCompressing] = useState(false)
    const [size, setSize] = useState(0);
    const [language, setLanguage] = useState(null);
    const languageOptions = [
        { label: 'English', value: 'en' },
        { label: 'Chinese', value: 'zh' },
        { label: 'Arabic', value: 'ar' },
        { label: 'Russian', value: 'ru' },
        { label: 'French', value: 'fr' },
        { label: 'German', value: 'de' },
        { label: 'Spanish', value: 'es' },
        { label: 'Portuguese', value: 'pt' },
        { label: 'Italian', value: 'it' },
        { label: 'Japanese', value: 'ja' },
        { label: 'Korean', value: 'ko' },
        { label: 'Greek', value: 'el' },
        { label: 'Dutch', value: 'nl' },
        { label: 'Hindi', value: 'hi' },
        { label: 'Turkish', value: 'tr' },
        { label: 'Malay', value: 'ms' },
        { label: 'Thai', value: 'th' },
        { label: 'Vietnamese', value: 'vi' },
        { label: 'Indonesian', value: 'id' },
        { label: 'Hebrew', value: 'he' },
        { label: 'Polish', value: 'pl' },
        { label: 'Mongolian', value: 'mn' },
        { label: 'Czech', value: 'cs' },
        { label: 'Hungarian', value: 'hu' },
        { label: 'Estonian', value: 'et' },
        { label: 'Bulgarian', value: 'bg' },
        { label: 'Danish', value: 'da' },
        { label: 'Finnish', value: 'fi' },
        { label: 'Romanian', value: 'ro' },
        { label: 'Swedish', value: 'sv' },
        { label: 'Slovenian', value: 'sl' },
        { label: 'Persian/Farsi', value: 'fa' },
        { label: 'Bosnian', value: 'bs' },
        { label: 'Serbian', value: 'sr' },
        { label: 'Telugu', value: 'te' },
        { label: 'Punjabi', value: 'pa' },
        { label: 'Tamil', value: 'ta' },
        { label: 'Gujarati', value: 'gu' },
        { label: 'Urdu', value: 'ur' },
    ];

    function handleLanguageChange(selectedOption) {
        const selectedLanguage = selectedOption ? selectedOption.value : '';
        setLanguage(selectedLanguage);
        console.log("Language:", language)
        console.log("selLanguage:", selectedLanguage)
    }
    // Create a project 
    async function handleCreateProject(title, language, media) {
        console.log("Creating new project with title:", title, "and file:", media);
        const formData = new FormData();
        formData.append("project_name", title)
        formData.append('project_file', media);
        if (language) {
            formData.append('language', language);
        }
        const response = await fetch(`${base_backend_url}/projects/create/${currentUser.userID}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
              },
            method: 'POST',
            body: formData
          });

        if (response.ok) {
            const result = await response.json()
            setShowPopup(false);
            setCurrentUser(currentUser => {
                console.log("User before:", currentUser)
                let newUser = {
                    ...currentUser,
                    currentProject: {
                        ...currentUser.currentProject,
                        projectName: title,
                        projectID: result.project.projectID,
                        originalVideoFileUrl: result.project.videoUrl,
                        videoURL: result.project.videoUrl,
                        videoFile: null,
                        originalVideoFile: null,
                        videoSize: media.size
                    }
                }
                console.log("User after:", newUser)
                return newUser
            })
            navigate('/project');
            setShowPopup(false); 
        } else {
            console.warn("Failed to add new project")
        }
        
    };

    const handleBack = () => {
        setShowPopup(false);
    };

    const handleSubmit = (event) => {
        event.preventDefault();
      
        // Get the form data
        const formData = new FormData(event.target);
      
        // Get the values
        const title = formData.get('title');
        const media = formData.get('media')
        setSize(media.size);
        setIsCompressing(true)
        handleCreateProject(title, language, media);
      };
      

    return (
        <div className="recent-project">
            <IconButton style={{left:"45%"}} onClick={() => setShowPopup(true)}>
                <AddIcon  className='project-delete-btn' style={{backgroundColor:"black",color:"white"}}/>
            </IconButton>
            <button onClick={() => setShowPopup(true)} className='thumbnail-btn'>
                
                <img src={newprojecticon} alt="New Project"/>
            </button>
            <div className='recent-prject-bottom-row'>
                <h1>New Project</h1>
            </div>
            
            <Modal 
                isOpen={showPopup}
                onRequestClose={handleBack}
                className="new-project-popup"
            >
                <div className="new-project-popup-content">
                    <button className="backButton" onClick={handleBack}>X</button>
                    <form onSubmit={handleSubmit} className='new-project-form'>

                    <label htmlFor="title">Project title:</label>
                    <input type="text" id="title" name="title" required />
                    <label htmlFor="language">Video language (<em>optional</em>)</label>
                    <Select
                        value={languageOptions.find(option => option.value === language)}
                        onChange={option => handleLanguageChange(option)}
                        options={languageOptions}
                        className='language-select-box'
                    />
                    <label htmlFor="media">Upload Media: <Tooltip text="Upload .mp4 file"/></label>
                    <input type="file" id="media" name="media" required style={{width:"fit-content",color:"white"}}/>
                    <button type="submit" className="createUploadButton"> Create Project </button>

                    </form>
                    
                    {(isCompressing) && <ProgressWheel durationInSeconds={size/800000}/>}

                </div>
            </Modal>
        </div>
    );
}


export default NewProject;