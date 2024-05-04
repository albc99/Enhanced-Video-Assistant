import os
from ..database.connect_to_azure_blob import BLOB
from ..database.azure_blob import get_container_client,upload_video_to_blob, upload_image_to_blob
from ..utils.condense import compress_video
from ..utils.eva_project import EVAProject as EVA
from sqlalchemy.orm import Session
from sqlalchemy import text
import subprocess
from fastapi import HTTPException

# account_key = get_account_key(cursor=cursor,file_id=file_id)
account_key = "VcpA6pXx2VKNSSVbgHnbJisOI39bxKDSXCKeLuE+alSBsg+3VkwZdIpgxdaTj7rTbt3I3Ay84JM9+AStTzahag==x" 

DOCKER_FILE_DIRECTORY = "/code/app/uploads/"

BLOB_VIDEO_URL = "https://tsmevastorage.blob.core.windows.net/srceva/"

#step 3 : get container client
container_client = get_container_client(account_key=account_key)


class UserService():
    """
    User service class to handle user related operations
    """
    def __init__(self, id: int):
        self.id = id

    async def create_project(self, name: str, language: str, project_file: str, db: Session):
        """
        """
        blob = BLOB()
        addProjectQuery = text("""
                        INSERT INTO dbo.projects_table (user_id, project_name, video_url)
                        VALUES (:user_id, :project_name, :video_url)
                        """)
        
        # the url will have to be created on blob and then referenced here
        videoUrl = f"www.testvideourl/userid={self.id}/project_name={name}.com"

        # Here we will add a new project given the ownerID, project name, current date, etc.
        db.execute(addProjectQuery, {"user_id": self.id, "project_name": name, "video_url": videoUrl})

        selectID = text("""
                    SELECT TOP 1 project_id 
                    FROM dbo.projects_table 
                    WHERE user_id = :user_id AND project_name = :project_name
                    ORDER BY project_id DESC;
                    """)
        result = db.execute(selectID, {"user_id": self.id, "project_name": name})
        x = result.fetchall()

        projectId = x[0][0]

        blob.createSave(projectId, language=language)

        updated_url = BLOB_VIDEO_URL + str(projectId) + ".mp4"

        try:
            name = 'old' + str(projectId) + '.mp4'
            compressed_name = str(projectId) + '.mp4'
            if not os.path.exists(DOCKER_FILE_DIRECTORY):
                os.mkdir(DOCKER_FILE_DIRECTORY)
            download_path = os.path.join(DOCKER_FILE_DIRECTORY, name)

            with open(download_path, 'wb') as f:
                f.write(await project_file.read())
            
            thumbnail_path = create_thumbnail(download_path, projectId) 
            await upload_image_to_blob(container_client, thumbnail_path, projectId)

            # upload to blob

            #os.remove(thumbnail_path)
            compressed_download_path = os.path.join(DOCKER_FILE_DIRECTORY, compressed_name)

            compress_video(download_path, compressed_download_path, 32)
            os.remove(download_path)
            updated_url = await upload_video_to_blob(container_client, compressed_download_path, projectId)

        except Exception as e:
            raise e

        updateProjectURL = text("""
                            UPDATE dbo.projects_table
                            SET video_url = :updated_url
                            WHERE project_id = :project_id
                            """)
        db.execute(updateProjectURL, {"updated_url": updated_url, "project_id": projectId})
        db.commit()

        return projectId, updated_url

    async def load_project(self,project_id:int):    
        blob = BLOB()
        project_data_blob = blob.load(project_id)
        #if audio isnt set to true/fasle, it means that load_media is never called
        #if it is set and for some reason, transcript (if vid has audio) 
        # or indexexer_result (if vid has no audio) are none, load_media should be called
        if (project_data_blob["audio"] is None or  (project_data_blob["transcript"] is None and project_data_blob["indexer_result"] is None)):
            eva = EVA(project_id=project_id)
            await eva.load_media(local_url = (DOCKER_FILE_DIRECTORY + str(project_id) + ".mp4"),filename=str(project_id))
            project_data_blob = blob.load(project_id)

        return project_data_blob
    
    async def save_project(self, projectData):
        blob = BLOB()
        await blob.save(projectData)

    def delete_project(self, id: int, db: Session):
        blob = BLOB()
        blob.deleteSave(id)

        deleteProjectQuery = text("""
                            DELETE FROM dbo.projects_table
                            WHERE project_id = :project_id
                            """)
        db.execute(deleteProjectQuery, {"project_id": id})
        db.commit()
        content = {"message": "Successfully deleted project!"}
        return content

    def get_all_projects(self, db: Session):
        query = text("SELECT * FROM dbo.projects_table WHERE user_id=:user_id")
        result = db.execute(query, {"user_id": self.id})

        projectList = []
        for project in result:
            projectObj = {
                "project_id": project[0],
                "projectName": project[2],
                "projectURL" : project[3],
                "videoUrl": project[-1]
            }
            projectList.append(projectObj)

        return projectList

    def get_current_project(self):
        return self.current_project

    def get_project_data(self, project_id):
        blob = BLOB()
        data = blob.load(project_id)
        return data
    

def create_thumbnail(download_path, project_id):
    # Create a thumbnail for the video
    print("Creating thumbnail for video", download_path)
    thumbnail_path = os.path.join(DOCKER_FILE_DIRECTORY, ('thumbnail' + str(project_id) + '.jpeg'))
    try:
        command = f'ffmpeg -ss 00:00:01.000 -i {download_path} -vf "scale=480:480:force_original_aspect_ratio=decrease" -vframes 1 {thumbnail_path}'
        subprocess.run(command, shell=True, check=True)

        print(f'Created thumbnail at path {thumbnail_path}')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading video: {str(e)}")

    return thumbnail_path
        