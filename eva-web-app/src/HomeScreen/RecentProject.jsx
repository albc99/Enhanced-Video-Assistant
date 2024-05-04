import { useContext, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { CurrentUserContext } from '../CurrentUserContext';
import './Project.css';
import { IconButton } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import Modal from 'react-modal';
import VideoThumbnail from './VideoThumbnail';

/**
 * RecentProject is a functional component that represents a recent project in the user's project list.
 *
 */
function RecentProject({projectTitle, projectId, projectURL, onDelete, thumbnailSrc}) {
    console.log("Project ID in RecentProject:", projectId);
    const {currentUser, setCurrentUser} = useContext(CurrentUserContext)
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [showNotification, setShowNotification] = useState(false);
    const navigate = useNavigate()
    const buttonRef = useRef();

    function onLaunchProject(e) {
        console.log("Launching project: " + projectTitle)
        let updateObject = {
            currentProject: {
                projectName: projectTitle,
                projectID: projectId,
                videoFile: null,
                originalVideoFile: null, 
                videoURL: projectURL,
                originalVideoFileUrl: projectURL,
                newProject: false
            }
        }
        console.log(projectURL)
        setCurrentUser(currentUser => ({
            ...currentUser,
            ...updateObject
        }))

        navigate(`/project`)
        setIsModalOpen(false);
    }
    // handleDelete is used to delete the project
    const handleDelete = () => {
        onDelete(projectId);
        setIsModalOpen(false);
        console.log("Deleting project ID:", projectId);

        setShowNotification(true);

        setTimeout(() => {
            setShowNotification(false);
        }, 5000);
    };

    // Functions for Modal
    const openModal = () => {
        setIsModalOpen(true);
    };
    
    const handleBack = () => {
        setIsModalOpen(false);
    };

    return (
        <div className="recent-project">
            {showNotification && 
            <div className="notificationBox">
                Project "{projectTitle}" has been deleted.
            </div>
            }
            <IconButton onClick={openModal} style={{left:"45%"}} >
                <DeleteIcon  className='project-delete-btn'/>
            </IconButton>
            <button ref={buttonRef} onClick={onLaunchProject} className='thumbnail-btn' >
                    {projectURL && <VideoThumbnail videoUrl={'https://tsmevastorage.blob.core.windows.net/srceva/' + projectId + 'img.jpeg'} buttonRef={buttonRef}/>}
            </button>
            <div className='recent-prject-bottom-row'>
                <h1>{projectTitle}</h1>
            </div>
            <Modal 
                isOpen={isModalOpen}
                onRequestClose={handleBack}
                className="delete-project-popup"
            >
                <div className="delete-project-popup-content">
                
                    <p>Are you sure you want to delete this project?</p>
                    <div className="delete-project-popup-button-container">
                        <button onClick={handleDelete}>Yes</button>
                        <button onClick={handleBack}>No</button>
                    </div>
                </div>
            </Modal>
        </div>
    )
}


export default RecentProject;