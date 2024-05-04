import React, { useState } from 'react';
import './FocusGroup.css'; 
import { useEffect, useContext } from 'react';
import { CurrentUserContext } from '../../../CurrentUserContext';
import { FeaturesDataContext } from '../../../FeaturesDataContext';
import base_backend_url from '../../../base_backend_url';
import ChatBox from './ChatBox';
import Tooltip from '../../../components/tooltip.jsx'

/**
 * FeedbackFG is a functional component that handles the feedback section of the focus group page.
 *
 */
function FeedbackFG({currentUser,isLoading,setIsLoading,chatLoading, setChatLoading, expandChat}){
  const [activeSection, setActiveSection] = useState('clarity');
  const {focusGroupData,isLoadingFeatureData,setChatMessages,chatMessages} = useContext(FeaturesDataContext);
  const [isChatExpanded, setIsChatExpanded] = useState(false);

  const toggleChatbox = () => {
    console.log('expandChat defined:', expandChat);
    if (expandChat) {
      expandChat(true); 
    }
  };
  
  useEffect(() => {
    setIsLoading(isLoadingFeatureData);
  }, [isLoadingFeatureData]);

    // This function sends the user's message to the backend and gets a response from GPT
    function sendToGPT(section, sectionFeedback) {
      setChatLoading(true);
      toggleChatbox();
      const question = "Give me tips to improve " + section + " in my video based off this feedback I got: ";
      const query = question + sectionFeedback;

      fetch(`${base_backend_url}/eva/focus_group_chat/${currentUser.userID}/${currentUser.currentProject.projectID}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({"query": query})
      })
      .then(response => response.json())
      .then(data => {
        // Add the user's message and EVA's response to the messages state
        setChatMessages(prevMessages => [
          ...prevMessages, 
          { user: 'User', text: question },
          { user: 'EVA', text: data.chat_response }
        ]);
        setChatLoading(false);
      });
    }
    // rendering feedback based on what section is active
    const renderFeedback = () => {
      if (isLoading) {
        return <div className='loading'></div>;
      }
      
      if (focusGroupData.feedback.length === 0) {
        return <p>No feedback available yet.</p>;
      }
      let content;
      switch (activeSection) {
        case 'tone':
          const feedbackContent = `
              Dominant Sentiment: ${focusGroupData.feedback.dominant_sentiment.charAt(0).toUpperCase() + focusGroupData.feedback.dominant_sentiment.slice(1)}
              Overall Tone Score: ${focusGroupData.feedback.sentiment_score.positive-focusGroupData.feedback.sentiment_score.negative+0.5*focusGroupData.feedback.sentiment_score.neutral}/10
              Overall Positive Sentiment: ${focusGroupData.feedback.sentiment_percentages.positive}%
              Overall Neutral Sentiment: ${focusGroupData.feedback.sentiment_percentages.neutral}%
              Overall Negative Sentiment: ${focusGroupData.feedback.sentiment_percentages.negative}%
              Current Tone Score: ${focusGroupData.tone_feedback.tone_score}%
              Tone Tip: ${focusGroupData.tone_feedback.tone_tips}
              `;
          content = (
            <div className="feedback-section">
                <div className="feedback-content"> 
                  <p><strong>Overall Tone Score:</strong> {focusGroupData.feedback.sentiment_score.positive-focusGroupData.feedback.sentiment_score.negative+0.5*focusGroupData.feedback.sentiment_score.neutral}/10</p>
                  <p><strong>Cuurent Tone Score:</strong>{focusGroupData.tone_feedback.tone_score}</p>
                  <p><strong>Tone Tips:</strong>{focusGroupData.tone_feedback.tone_tips}</p>
                </div>
                <button className="send-to-gpt-btn" title="Tone feedback" onClick={() => sendToGPT('tone', feedbackContent)}>Tips to improve tone</button>
              </div>
          );
          break;
          case 'clarity':
            const clarityFeedbackContent = `
              Overall Clarity Score: ${focusGroupData.feedback["Clarity Score"]}
              Clarity Tip: ${focusGroupData.feedback["Clarity Tip"]}
            `;
            content = (
              <div className="feedback-section">
                  <div className="feedback-content">
                    <p><strong>Overall Clarity Score:</strong> {focusGroupData.feedback["Clarity Score"]}</p>
                    <p><strong>Clarity Tip:</strong> {focusGroupData.feedback["Clarity Tip"]}</p>
                  </div>
                  <button className="send-to-gpt-btn" title="Clarity feedback" onClick={() => sendToGPT('clarity', clarityFeedbackContent)}>Tips to improve clarity</button>
              </div>
            );
            break;
          case 'engagement':
            const engagementFeedbackContent = `
              Overall Engagement Score: ${focusGroupData.feedback["Engagement Score"]}
              Engagement Tip: ${focusGroupData.feedback["Engagement Tip"]}
            `;
            content = (
              <div className="feedback-section">
                  <div className="feedback-content">
                    <p><strong>Overall Engagement Score:</strong> {focusGroupData.feedback["Engagement Score"]}</p>
                    <p><strong>Engagement Tip:</strong> {focusGroupData.feedback["Engagement Tip"]}</p>
                    
                  </div>
                  <button className="send-to-gpt-btn" title="Engagement feedback" onClick={() => sendToGPT('engagement', engagementFeedbackContent)}>Tips to improve engagement</button>
              </div>
            );
            break;
        default:
          content = <p>Invalid section</p>;
      }
      
          return content;
        };

    return (

      <div className='focusgroup-feedback-container'>
            <div className="tabs">
              <button className={activeSection === 'tone' ? 'active' : ''} onClick={() => setActiveSection('tone')}>Tone</button>
              <button className={activeSection === 'clarity' ? 'active' : ''} onClick={() => setActiveSection('clarity')}>Clarity</button>
              <button className={activeSection === 'engagement' ? 'active' : ''} onClick={() => setActiveSection('engagement')}>Engagement</button>
            </div>
            {!isLoading ? (
              <div className="content">
              {renderFeedback()}
            </div>

            ) : (
              //Loading Case
              <div className="content" style={{ alignItems: 'center', justifyContent: 'center' }}>
                {renderFeedback()}
              </div>
            )
            }
          </div>
    );
}


function FocusGroup() {
    const [isLoading, setIsLoading] = useState(false);
    const [chatLoading, setChatLoading] = useState(false);
    const {focusGroupData, setFocusGroupData} = useContext(FeaturesDataContext);
    const {currentUser, setCurrentUser} = useContext(CurrentUserContext);
    const [isChatExpanded, setIsChatExpanded] = useState(false);
    const [expandChat, setExpandChat] = useState(null);

    // called when generate button is clicked, grabs data from backend
    const handleGenerate = () => {
      console.log('Before fetch, feedback state is:', focusGroupData);
      //setTimestamps({'timestamps': [[10, 20]]});
      setIsLoading(true);
      fetch(`${base_backend_url}/eva/focus_group/${currentUser.userID}/${currentUser.currentProject.projectID}`, {
        
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({"scrubber_timestamps": []})
      })
      .then(response => response.json())
      .then(data => {
        console.log(data);
        if (data.feedback || data.clip_tones) {
          setFocusGroupData(currentState => ({
            ...currentState,
            feedback: data.feedback ? data.feedback : currentState.feedback,
            clip_tones: data.clip_tones ? data.clip_tones : currentState.clip_tones,
            tone_feedback: {
              tone_score: data.tone_feedback?.["Tone Score"] || currentState.tone_feedback?.tone_score,
              tone_tips: data.tone_feedback?.["Tone Feedback"] || currentState.tone_feedback?.tone_tips
            }
          }));
        }
        console.log('After setFeedback, feedback state should be:', focusGroupData);
      })
      .catch(error => {
        console.error('Error:', error);
      })
      .finally(() => {
        setIsLoading(false); 
      });
  };
  return (
    <div className="focus-group">
          <h2>Focus Group</h2>
          <ChatBox 
          className={isChatExpanded ? 'chatbox-expanded' : 'chatbox-collapsed'}
          onClick={() => setIsChatExpanded(!isChatExpanded)}
          chatLoading={chatLoading} 
          setChatLoading={setChatLoading} 
          setIsChatDirectlyExpanded={setExpandChat}
          currentUser={currentUser} 
        />
          <FeedbackFG isLoading={isLoading} setIsLoading={setIsLoading} 
                      chatLoading={chatLoading} setChatLoading={setChatLoading}
                      expandChat={expandChat}
                      currentUser={currentUser}/>
<button className="fg-generate-btn" disabled={!currentUser.currentProject.isUploaded || isLoading} title={!currentUser.currentProject.isUploaded ? "Video is uploading..." : ""} onClick={handleGenerate}>Generate Feedback <Tooltip text="Generates automated feedback based on current video"/></button>    </div>
      );
      
}

export default FocusGroup;
