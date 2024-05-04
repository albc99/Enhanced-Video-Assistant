import { useContext, useState } from 'react';
import { useNavigate } from "react-router-dom";
import axios from 'axios';
import base_backend_url from '../../../base_backend_url';
import { CurrentUserContext } from '../../../CurrentUserContext';
import './Dropdown.css';
import {FeaturesDataContext} from '../../../FeaturesDataContext.jsx';

function ProfileDropdown({logoutHandler }) {
    const navigate = useNavigate();
    
    const { streamlinerData, narrationImproverData, focusGroupData } = useContext(FeaturesDataContext);
    

  


    return (
        <div className="profile-dropdown">
           
        </div>
    );
}

export default ProfileDropdown;


