from fastapi import APIRouter, HTTPException, UploadFile, File, Form,Depends
from fastapi.responses import JSONResponse
from ..database.azure_blob import * # this imports everything for Azure blob storage connection
from ..utils.user import UserService
from ..utils.schemas import SaveProjectData
from fastapi.params import Body
from typing import Dict,Optional
from ..database.database import get_db_connection
from sqlalchemy.orm import Session

"""
File: projects.py
Description: This file contains the functions that interact with the projects.
Functionality: This file is used to get, create, delete, load and save projects.
"""

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
def get_projects(user_id:int,db: Session = Depends(get_db_connection) ):
    try:
        user_service = UserService(id=user_id)
        project_list = user_service.get_all_projects(db)
        return JSONResponse(content={"message": "successfully got user projects","projects": project_list})
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/create/{user_id}")
async def create_project( user_id:int,project_name: str = Form(... ), project_file : UploadFile = File(...),
                         language:Optional[str] = Form(None),db: Session = Depends(get_db_connection)):
    # Fetch the user from the database
    try:
        user_service = UserService(id=user_id)
        project_id, video_url = await user_service.create_project(name=project_name, project_file=project_file,language=language,db=db)
        print(project_id, video_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"message": "Successfully added project!",
        "project": {
            "projectName": project_name,
            "videoUrl": video_url,
            "projectID": project_id
        }
    })    


@router.delete("/delete/{user_id}/{project_id}")
def delete_project(user_id:int,project_id: int,db: Session = Depends(get_db_connection)):
   
    try:
        user_service = UserService(id=user_id)
        user_service.delete_project(project_id,db=db)
        return JSONResponse(content={"message": "Successfully deleted project!"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/load_project/{user_id}/{project_id}")
async def load_project(user_id:int,project_id:int):    
    try:
        user_service = UserService(id=user_id)
        project_data = await user_service.load_project(project_id)
        return JSONResponse(content={"message": "Successfully loaded project!",
                                     "streamlinerData":project_data["streamlinerData"],
                                     "narrationImproverData":project_data["narrationImproverData"],
                                     "focusGroupData":project_data["focusGroupData"]})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/save_project/{user_id}/{project_id}")
def save_project(user_id:int,project_id:int,data : SaveProjectData):    
    try:
        data_dict = data.dict()
        data_dict["projectID"] = project_id
        user_service = UserService(id=user_id)
        user_service.save_project(data_dict)
        return JSONResponse(content={"message": "Successfully saved project!"},status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post('/get_project_data/{user_id}/{project_id}')
def get_project_data(user_id:int,project_id:int):
    try:
        user_service = UserService(id=user_id)
        project_data = user_service.get_project_data(project_id)
        return project_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))