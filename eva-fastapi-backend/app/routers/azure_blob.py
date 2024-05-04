from ..database.azure_blob import *
import os
from fastapi import APIRouter, HTTPException, UploadFile, HTTPException, Form, File, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing_extensions import Annotated
from azure.storage.blob import BlobClient

"""
File: azure_blob.py
Description: This file contains the functions that interact with the Azure Blob Storage.
Functionality: This file is used to upload the video and image files to the Azure Blob Storage.
"""


# GLobal variables
username = "tsm-admin"
password = "EVAisAwesome!"
account_name="tsmevastorage"
container_name="srceva"
docker_file_directory = "/code/app/uploads/"

#step 1 : get cursor, file id from sql DB
# cursor, file_id = get_cursor_fileid(username=username,password=password)

#step 2 : get account key
# account_key = get_account_key(cursor=cursor,file_id=file_id)
account_key = "VcpA6pXx2VKNSSVbgHnbJisOI39bxKDSXCKeLuE+alSBsg+3VkwZdIpgxdaTj7rTbt3I3Ay84JM9+AStTzahag==x" 

#step 3 : get container client
container_client = get_container_client(account_key=account_key,account_name=account_name,container_name=container_name)


router = APIRouter(
    prefix="/azure_blob",
    tags=["azure_blob"],
    responses={404: {"description": "Not found"}},
)

class UploadRequest(BaseModel):
    filepath: str

class DownloadRequest(BaseModel):
    filename: str

# @router.post("/download_video")
# async def download_video(download_request: DownloadRequest):
@router.post("/download_video")
async def download_video(data : dict):
    try:
        name = str(data['name'])
        name = name + '.mp4'
        download_path = os.path.join(docker_file_directory, name)

        if not os.path.exists(download_path):
            with open(download_path, "wb") as my_blob:
                connection_string = 'DefaultEndpointsProtocol=https;AccountName=' + 'tsmevastorage' + ';AccountKey=' + 'VcpA6pXx2VKNSSVbgHnbJisOI39bxKDSXCKeLuE' + ';EndpointSuffix=core.windows.net'
                blob_url = data['url']
                blob_client = BlobClient.from_blob_url(blob_url, connection_string=connection_string)
                download_stream = blob_client.download_blob()
                my_blob.write(download_stream.readall())

        # uploaded_video = UploadFile(filename="downloaded_video.mp4", headers = headers_list, file=response.content)
        return JSONResponse(content={"message": "Video downloaded successfully"},status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading video: {str(e)}")

#https://stackoverflow.com/questions/72685197/upload-files-from-fastapi-to-azure-blob-storage
# https://stackoverflow.com/questions/72685197/upload-files-from-fastapi-to-azure-blob-storage
@router.post("/upload_video")
async def create_upload_file(video: UploadFile = File(...), pid: str = Form(...)):
    try:
        blobUrl = await upload_video_to_blob(container_client, video, pid)

        return {"videoUrl" : blobUrl}
    except Exception as e:
        print(e)
        raise HTTPException(401, "Something went terribly wrong..")

@router.post('/upload_to_backend')
async def upload_to_backend(video: UploadFile):
    print("upload is", video)


    try:
        print("Received video on backend!")
        # Save the file to the server
        if not os.path.exists(docker_file_directory):
            os.mkdir(docker_file_directory)

        destinationPath = os.path.join(docker_file_directory, video.filename)
        
        with open(destinationPath, 'wb') as f:
            f.write(await video.read())
        print(f'Saved video to path {destinationPath}')
        
        # response = await load_media(LoadMediaRequest(media_filename=str(video.filename),blob_url=" "))
        return {
            'message': 'File uploaded successfully',
            
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading video: {str(e)}")
    
@router.get('/get_current_video/')
async def get_video(videoname: Annotated[str, Query()]):
    requestedPath = os.path.join(docker_file_directory, videoname)
    print(requestedPath)
    if not os.path.exists(requestedPath):
        raise HTTPException(status_code=404, detail=f'Video not found in Docker storage at path {requestedPath}')
    return FileResponse(path=requestedPath)