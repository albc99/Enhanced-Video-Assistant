import os
from fastapi import APIRouter, HTTPException, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import List,Optional
from ..utils.eva_project import EVAProject

"""
File: eva.py
Description: This file contains the functions that interact with the EVA Project.
Functionality: This file is used to streamline the video, improve the narration, run focus group, generate video and normalize the audio.
"""

router = APIRouter(
    prefix="/eva",
    tags=["eva"],
    responses={404: {"description": "Not found"}},
)

class LoadMediaRequest(BaseModel):
    media_filename:str
    blob_url:str

class Timestamps(BaseModel):
    scrubber_timestamps: List[float]


@router.post("/streamline_video/{user_id}/{project_id}")
async def streamline_video(user_id:int,project_id:int):

    try:
        eva =EVAProject(project_id=project_id)
       # Generate the output path dynamically
        input_filename = os.path.basename(eva.media_path)
        filename = f"processed_{input_filename}"
        output_path = os.path.join("/code/app/uploads", filename)
        deleted_clips,important_clips = await eva.streamline_video()
        
        return JSONResponse(content={"message": "Video streamlined successfully","inputFile":input_filename ,"outputFilePath":output_path,"deleted_clip_timestamps":deleted_clips,"important_clip_timestamps":important_clips})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streamlining video: {str(e)}")
    
@router.post("/narration_improver/{user_id}/{project_id}")
async def narration_improver(user_id:int,project_id:int):
    try:
        eva =EVAProject(project_id=project_id)
        get_edits = await eva.improve_narration()
        return JSONResponse(content={"message": "Narration improved successfully","edits":get_edits})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running narration improver: {str(e)}")
    


@router.post("/focus_group/{user_id}/{project_id}")
async def focus_group_run(user_id:int,project_id:int,timestamps:Optional[dict]=None):
    try:
        eva =EVAProject(project_id=project_id)
        # eva.timestamps = timestamps
        feedback, clip_tones, tone_feedback = await eva.focus_group_run(timestamps["scrubber_timestamps"])
        return JSONResponse(content={"message": "Feedback from Focus group generaeted successfully","feedback":feedback, "clip_tones":clip_tones, "tone_feedback":tone_feedback})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running Focus group: {str(e)}")

@router.post("/focus_group_chat/{user_id}/{project_id}")
async def focus_group_chat(user_id:int,project_id:int,query_data:Optional[dict]=None):
    try:
        eva =EVAProject(project_id=project_id)
        chat_response = eva.focus_group_chat(query_data["query"])
        return JSONResponse(content={"message": "Feedback for Focus group chat generaeted successfully","chat_response":chat_response})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running Focus group chat: {str(e)}")
    
@router.post("/generate_video/{user_id}/{project_id}")
async def generate_video(user_id:int,project_id:int,data: dict):
    print("gerneate video eva.py")
    eva =EVAProject(project_id=project_id)
    current_version_timestamps = data["scrubber_timestamps"]

    #convert to list of tuples format
    current_version_timestamps = list(zip(*[iter(current_version_timestamps)]*2))
    # Generate the output path dynamically
    input_filename = os.path.basename(eva.media_path)
    filename = f"processed_{input_filename}"
    output_path = os.path.join("/code/app/uploads", filename)

    try:
        await eva.generate_video(current_version_timestamps,output_file_path=output_path)
        
        if data["normalize_audio"]:
            try:
                await eva.normalize_output_media(output_file_path=output_path,remove_low_rumbling=False)
            except Exception as e:
                return JSONResponse(content={"message": "Video generaeted successfully but normalization failed","outputFilePath":output_path,"is_normalized":False, "Normalization error":str(e)})
            
        return JSONResponse(content={"message": "Video generaeted successfully and audio normalization applied","outputFilePath":output_path,"is_normalized":True})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating video: {str(e)}")
    


     