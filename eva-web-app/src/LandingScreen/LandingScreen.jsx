import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';
import projectPageImage from './ProjectPage.png';

/**
 * LandingScreen is a functional component that represents the landing screen of the application.
 */
function LandingScreen() {
    const navigate = useNavigate();
    // Switch to login page
    const navigateToLogin = () => {
        navigate('/login', { replace: true });
        };
      
      // Switch to register page
      const navigateToSignUp = () => {
        navigate('/signup', { replace: true });
      };
return (
    <div className="landing-page-container">

    <main className="main">
            <div className="main-card">
                    <div className="main-card-details">
                        <div style={{rowGap:"5vh"}}>
                                <h1 style={{fontSize: "42px"}}>Introducing the Enhanced Video Assistant (EVA)</h1>
                                <h2> Create high quality videos with minimal effort. </h2>
                        </div>
                        <div style={{width:"50%",display:"flex",justifyContent:"space-between",marginLeft:"25%"}}>
                                <button type="button" className="main-card-buy-button" onClick={navigateToLogin}>Login</button>
                                <button type="button" className="main-card-buy-button" onClick={navigateToSignUp}>SignUp</button>
                        </div>
                    </div>
                    <div className="demo-video-container">
                            <iframe className="demo-video" src="https://www.youtube.com/embed/327o4ebFC1o?si=amRSS-1Ru3OFl07g" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
                    </div>
            </div>
            <div className="features">
                    <h1 style={{marginLeft: "15vw", marginRight: "15vw",marginBottom:"10vh",fontSize:"2.4vw"}}>
                            Combining the convenience of advanced AI with a user-friendly interface
                    </h1>
                    <p style={{marginLeft: "22vw", marginRight: "22vw"}}>
                    EVA is an innovative video editing application designed to address common 
                    issues faced by content creators, educators, businesses, and even casual video makers.
                    </p>
                    <div className="feature-card">
                    <div className="feature-card-img-container">
                            <img className="feature-card-image" src={projectPageImage} alt="Feature"/>
                    </div>
                            <div className="feature-card-details">
                                    <h1 style={{marginBottom:"3vh"}}>Video Streamliner</h1>
                                    <p>Simplify content down to the essential details.  It's like having a personal assistant who sifts through your content 
                                            and selects the most important segments. </p>
                            </div>
                    </div>
                    <div className="feature-card">
                            <div className="feature-card-details">
                                    <h1 style={{marginBottom:"3vh"}}>Narration Improver</h1>
                                    <p>EVA will enhance your audio quality by removing or smoothing out mumbles and ensuring a consistent tone 
                                             throughout video. It's also equipped with an audio volume normalizer to provide a balanced audio experience for your viewers.</p>
                            </div>
                            <div className="feature-card-img-container">
                                    <img className="feature-card-image"src={projectPageImage}/>
                            </div>
                    </div>
                    <div className="feature-card">
                            <div className="feature-card-img-container">
                                    <img className="feature-card-image"src={projectPageImage}/>
                            </div>
                            <div className="feature-card-details">
                                    <h1 style={{marginBottom:"3vh"}}>AI Focus Group</h1>
                                    <p> Helps you ensure your intended audience will stick with your video right to the end and walk away with the 
                                            message you wanted to deliver. Gives feedback on  factors such as Tone, Clarity and Engagement.</p>
                            </div>
                    </div>
            </div>

            <div className="divider">
            {Array(25).fill().map((_, index) => (
                    <div key={index} className="square-box"></div>
            ))}
            </div>
            <div className="example-container">
                    <h1>EVA EVA EVA EVA EVA</h1>
                    <img 
                            style={{width:"70vw", height:"70vh", marginTop: "5vh", marginBottom: "5vh"}}
                            src="https://cdn.mos.cms.futurecdn.net/mW3AwP3QC4HgWqAaGeQcwF.jpg" 
                            alt="EVA"
                    />
                    <h2 style={{marginLeft: "22vw", marginRight: "22vw"}}>
                            [placeholder]EVA is an innovative video editing application designed to address common 
                            issues faced by content creators, educators, businesses, and even casual video makers.
                    </h2>
            </div>
            </main>
    </div>
);
}

export default LandingScreen;