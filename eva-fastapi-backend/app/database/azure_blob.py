from azure.storage.blob import BlobServiceClient
import json

"""
File: azure_blob.py
Description: This file contains the functions that interact with the Azure Blob Storage.
Functionality: This file is used to upload the video and image files to the Azure Blob Storage.
"""

with open('credentials.json', 'r') as file:
    data = json.load(file)

# Assign values from the JSON file to variables
key = data['key']
username = data['username']
password = data['password']
account_name = data['account_name']
container_name = data['container_name']

def get_container_client(account_key,account_name="tsmevastorage",container_name="srceva"):
    """
    Connect to blob continaer and Get container client
    """
    blob_service_client = get_service_client(account_key,account_name=account_name,container_name=container_name)

    #use the client to connect to the container
    container_client = blob_service_client.get_container_client(container_name)
    return container_client

def get_service_client(account_key,account_name,container_name):
    """
    Connect to blob service and get service client
    """

    #create a client to interact with blob storage
    connect_str = 'DefaultEndpointsProtocol=https;AccountName=' + account_name + ';AccountKey=' + account_key + ';EndpointSuffix=core.windows.net'
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    return blob_service_client


async def upload_video_to_blob(container_client, video, projectId):
    id = str(projectId) + ".mp4"
    blob_client = container_client.get_blob_client(id)
    print("Got blob client")
    print("Upload file:", video)
    print("Video was read to bytes")
    with open(video, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    return blob_client.url


async def upload_image_to_blob(container_client, image, projectId):
    id =  str(projectId) + "img.jpeg"
    blob_client = container_client.get_blob_client(id)
    print("Got blob client")
    print("Upload file:", image)
    with open(image, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    return blob_client.url