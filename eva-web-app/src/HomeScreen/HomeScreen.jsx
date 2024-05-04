import React, { useState, useContext, useEffect } from 'react';
import RecentProject from './RecentProject.jsx'
import NewProject from './NewProject.jsx'
import base_backend_url from '../base_backend_url.js';
import './HomeScreen.css';
import { CurrentUserContext } from '../CurrentUserContext.jsx';
import ProjectSkeleton from './ProjectSkeleton.jsx';
import { useNavigate } from 'react-router-dom';
import AccountBoxIcon from '@mui/icons-material/AccountBox';

/**
 * HomeScreen is a functional component that represents the home screen of the application.
 *
 */
async function GetUserProjects(userId) {
    let destinationUrl = `${base_backend_url}/projects/?user_id=${userId}`
    const response = await fetch(destinationUrl, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
    })

    const result = await response.json()

    if (response.ok) {
        return result
    } else {
        console.log("Failed to retrieve project for user: " + result.message)
    }
}

function HomeScreen() {
    const {
        currentUser,
        setCurrentUser
    } = useContext(CurrentUserContext)

    const [projects, setProjects] = useState(null)
    const [needsUpdate, setNeedsUpdate] = useState(true)
    const [sortOption, setSortOption] = useState('None')

    let sortedProjects = Array.isArray(projects) ? [...projects] : [];
    if (sortOption === 'A-Z') {
        sortedProjects.sort((a, b) => a.projectName.localeCompare(b.projectName));
    } else if (sortOption === 'Z-A') {
        sortedProjects.sort((a, b) => b.projectName.localeCompare(a.projectName));
    }

    const dummyProjects = [
        {
            projectName: 'Project1'
        }, 
        {
            projectName: 'Project2'
        },
        {
            projectName: 'Project3'
        },
        {
            projectName: 'Project4'
        }
    ]
    // Handles logging out of the application and switching off the user
    function LogoutButton({ username, onLogout }) {
        const navigate = useNavigate();
    
        const handleLogout = () => {
            console.log('Logging out');
            if (onLogout) {
                onLogout(); // updating state in app.jsx
            }
            localStorage.removeItem('token');
            localStorage.removeItem('currentUser');
            navigate('/login');
        };
    
        return (
            <div>
                <button className="logout-button" onClick={handleLogout}>
                    <span>Logout</span>
                </button>
            </div>
        );
    }

    useEffect(() => {
        if (needsUpdate) {
            console.log("Needs update")
            if (currentUser.userID === null) {
                setNeedsUpdate(false)
                setProjects(dummyProjects)
                return
            }
            console.log(currentUser)
            console.log("Updating projects")
            let ignore = false;

            GetUserProjects(currentUser.userID).then((result) => {
                if (!ignore) {
                    setNeedsUpdate(false)
                    console.log(result);

                    if (result != null) {
                        setProjects(result.projects)
                    }
                    else {
                        setProjects([])
                    }
                }
            });

            return () => { 
                ignore = true
            }
        }
    }, [currentUser, needsUpdate])
        
    // This function is used to delete a project from the database
    const handleDeleteProject = async (projectId) => {
        console.log("Attempting to delete project with ID:", projectId);
        const response = await fetch(`${base_backend_url}/projects/delete/${currentUser.userID}/${projectId}`, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
              },
          method: 'DELETE',
        });
      
        if (response.ok) {
          setNeedsUpdate(true);
        } else {
          console.warn('Failed to delete project');
        }
    };

    return (
        <div className="homescreen">
            <div className='homescreen-top-row'>
                <LogoutButton/>
                <div className="current-user-container">
                    <AccountBoxIcon style={{color:"#cfb456",height:"20%", width:"20%"}}></AccountBoxIcon>
                    <h3 >{currentUser.username ? currentUser.username : "user"}</h3>
                </div>
            </div>
            <div className="homescreen-title">
                <h1>Welcome to EVA!</h1>
            </div>
            
            <div className="line"></div>
            <div className="recent-projects-parent">
                <h2 className="recent-projects-label">Recent Projects</h2>
                <div className="sort-container">
                    <label>Sort by:</label>
                    <select value={sortOption} onChange={(e) => setSortOption(e.target.value)}>
                        <option value='None'>None</option>
                        <option value='A-Z'>Name (A-Z)</option>
                        <option value='Z-A'>Name (Z-A)</option>
                    </select>
                </div>
                <div className="recent-projects-container">
                    <NewProject/>
                    {projects == null ? 
                        <ProjectSkeleton/>
                        : sortedProjects.map(project => (
                        <RecentProject 
                            key={project.project_id} 
                            projectTitle={project.projectName}
                            projectId={project.project_id}
                            projectURL={project.projectURL}
                            onDelete={handleDeleteProject}
                        />
                    ))}
                </div>   
            </div>
        </div>
    )
}


export default HomeScreen
