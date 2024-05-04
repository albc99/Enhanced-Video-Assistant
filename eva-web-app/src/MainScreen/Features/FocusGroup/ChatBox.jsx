import React, { useState, useContext, useEffect, useRef } from 'react';
import './ChatBox.css'; // Import your CSS file for styling
import SendIcon from '@mui/icons-material/Send';
import DeleteIcon from '@mui/icons-material/Delete';
import base_backend_url from '../../../base_backend_url';
import { FeaturesDataContext } from '../../../FeaturesDataContext';
import ChatIcon from '@mui/icons-material/Chat';
import ExpandCircleDownIcon from '@mui/icons-material/ExpandCircleDown';

/**
 * ChatBox is a functional component that handles the chat box in the application.
 *
 */
const ChatBox = ({chatLoading, setChatLoading,currentUser, setIsChatDirectlyExpanded}) => {

  const {chatMessages,setChatMessages} = useContext(FeaturesDataContext);
  const [isChatExpanded, setIsChatExpanded] = useState(false);
  const chatOutputRef = useRef(null);

  useEffect(() => {
    if (setIsChatDirectlyExpanded) {
      setIsChatDirectlyExpanded(() => setIsChatExpanded); 
    }
  }, [setIsChatDirectlyExpanded, setIsChatExpanded]);

    const handleClearHistory = () => {
        setChatMessages([]);
      };

    const handleSend = (event) => {
        event.preventDefault();
        setChatLoading(true);
        const userInput = event.target.userInput.value;
        fetch(`${base_backend_url}/eva/focus_group_chat/${currentUser.userID}/${currentUser.currentProject.projectID}`, {          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({"query": userInput})
        })
        .then(response => response.json())
        .then(data => {
          // Add the user's message and EVA's response to the messages state
          setChatMessages(prevMessages => [
            ...prevMessages, 
            { user: 'User', text: userInput },
            { user: 'EVA', text: data.chat_response }
          ]);
          setChatLoading(false);
        });
        // Clear the input field after the request has been sent and a response has been received
      event.target.userInput.value = '';
      };

      const toggleChatbox = () => {
        setIsChatExpanded(!isChatExpanded);
    
        if (isChatExpanded) {
          setTimeout(() => {
            const chatbox = document.querySelector('.chatbox-expanded, .chatbox-collapsed');
            if (chatbox) {
              chatbox.style.width = '';
              chatbox.style.height = '';
              chatbox.style.position = 'fixed';
              chatbox.style.bottom = '30px';
              chatbox.style.right = '30px';
            }
          }, 0);
        }
      };
      
      useEffect(() => {
        if (chatOutputRef.current) {
          chatOutputRef.current.scrollTop = chatOutputRef.current.scrollHeight;
        }
      }, [chatMessages]);
      
      return (
        <div className={isChatExpanded ? 'chatbox-expanded' : 'chatbox-collapsed'}>
          {isChatExpanded ? (
            <div className="chatbox-header">
              <span className="chatbox-title">Ask our AI audience</span>
              <button className="expand-circle-button" onClick={toggleChatbox}>
                <ExpandCircleDownIcon />
              </button>
            </div>
          ) : (
            <button className="chat-icon-button" onClick={toggleChatbox}>
              <ChatIcon />
            </button>
          )}
          {isChatExpanded && (
            <div className="chatbox-container">
              <form className="chatbox-input-form" onSubmit={handleSend}>
                <input className="chatbox-input" type="text" name="userInput" placeholder="Chat about video here..." />
                <button type="submit" className='chatbox-input-send' title="Send message"> 
                  <SendIcon />
                </button>
                <button type="button" onClick={handleClearHistory} style={{backgroundColor:"#cc3333"}}>
                  <DeleteIcon />
                </button>
              </form>
      
              <div className="chatbox-output" ref={chatOutputRef}>
                {chatMessages.map((message, index) => (
                  <p key={index} className={`message-text ${message.user === 'User' ? 'user-message' : 'eva-message'}`}>
                    <strong>{message.user}:</strong> {message.text}
                  </p>
                ))}
                {chatLoading && <p><strong>Loading....</strong></p>}
              </div>
            </div>
          )}
        </div>
      );
      
};

export default ChatBox;