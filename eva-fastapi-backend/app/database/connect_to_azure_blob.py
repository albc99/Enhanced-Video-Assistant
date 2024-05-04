from azure.storage.blob import BlobServiceClient
from pydantic import BaseModel
import json
from ..utils.schemas import ProjectJsonData,StreamlinerData,NarrationImproverData,FocusGroupData


class UploadBody(BaseModel):
    streamlinerData: str
    narrationImproverData: str
    focusGroupData: str

class BLOB():
  def __init__(self):
      
    with open('credentials.json', 'r') as file:
      data = json.load(file)

    # Assign values from the JSON file to variables
    self.key = data['key']
    self.username = data['username']
    self.password = data['password']
    self.account_name = data['account_name']
    self.container_name = data['container_name']

    return
  
  def createSave(self, id,language=None):
    account_name = self.account_name
    account_key = self.key
    
    blob_name = str(id) + ".json"  
    blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)
    blob_client = blob_service_client.get_blob_client(container="saves", blob=blob_name)
    project_json_data = ProjectJsonData(
        streamlinerData=StreamlinerData(),
        narrationImproverData=NarrationImproverData(),
        focusGroupData=FocusGroupData(),
        transcript=None,
        indexer_result=None,
        audio=None,
        language=language,
        scrubber_timestamps=None,
        summary=None
    )

    data = project_json_data.dict()
    json_string = json.dumps(data)
    bytes = json_string.encode('utf-8')

    blob_client.upload_blob(bytes, overwrite=True)

  
  def load(self, id):
    """
    load blob json of given id project
    """
    account_name = self.account_name
    account_key = self.key
    blob_name = str(id) + ".json"
    blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)
    blob_client = blob_service_client.get_blob_client(container="saves", blob=blob_name)

    blob_content = blob_client.download_blob().readall()
    json_data = json.loads(blob_content.decode("utf-8"))

    return json_data


  async def save(self, data):
    """
    save to blob
    """
    account_name = self.account_name
    account_key = self.key

    id = data["projectID"]
    blob_name = str(id) + ".json"

    del data["projectID"]

    blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)
    blob_client = blob_service_client.get_blob_client(container="saves", blob=blob_name)

    # Download the existing blob data
    download_stream = blob_client.download_blob()
    existing_data = json.loads(download_stream.readall().decode('utf-8'))

    # Update the specific keys in the JSON data
    for key in data:
        existing_data[key] = data[key]

    # Convert the updated data back to a JSON string
    json_string = json.dumps(existing_data)
    bytes = json_string.encode('utf-8')

    print("saving to blob")
    # Upload the updated JSON data back to the blob
    blob_client.upload_blob(bytes, overwrite=True)

    print("saved to blob")
    
  def deleteSave(self, id):
    account_name = self.account_name
    account_key = self.key

    blob_name = str(id) + ".json"

  
    blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)
    blob_client = blob_service_client.get_blob_client(container="saves", blob=blob_name)

    try: 
       blob_client.delete_blob()
    except Exception as e:
       print("ERROR deleting project id: ", id)


#used this tutotiral for getting file from blob storage
#https://www.youtube.com/watch?v=DrjIexCTF70
#For reading b yte data from the blob storage
#https://pub.towardsai.net/how-to-list-read-upload-and-delete-files-in-azure-blob-storage-with-python-836f8efa1c99
#For reading byte data from the blob storage
#https://pub.towardsai.net/how-to-list-read-upload-and-delete-files-in-azure-blob-storage-with-python-836f8efa1c99

#connecting to database with python
#https://stackoverflow.com/questions/33725862/connecting-to-microsoft-sql-server-using-python
#https://github.com/mkleehammer/pyodbc/issues/717

#Microsoft learn for uploading file  
#https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-upload-python


