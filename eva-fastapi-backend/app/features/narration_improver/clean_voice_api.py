import time
import requests
import os
import subprocess
import json


"""
File: clean_voice_api.py
Description: This file contains the functions that interact with the CleanVoice API.
Functionality: CleanVoice API is the main core of the narration improver feature. It is used to detect dead air, filler words, and other unwanted audio segments in the narration.
"""


#For converting audio to video
#https://www.youtube.com/watch?v=ucXTQ0V8qMA
def convert_video_to_audio(input_path, output_path):
    command = [
        'ffmpeg',
        '-i', input_path,
        "-vn",
        '-acodec', 'libmp3lame',
        "-ab", "192k",
        "-ar", "44100",
        "-y",
        output_path
    ]

    subprocess.run(command)

def get_narration_edits(input_file_path):
    with open('/features/credentials.json', 'r') as file:
        data = json.load(file)
    api_key = data['CLEAN_VOICE_API_KEY'] #Only good for 30 minutes of upload video, may need to make a new account on CleanVoiceAPI. 
    #Upload audio file to CleanVoice
    url = 'https://api.cleanvoice.ai/v1/upload?filename=file.m4a'
    headers = {'X-API-Key': api_key}
    response = requests.post(url, headers=headers)
    signed_url = response.json()['signedUrl'] #Temporary url for file upload
    file = open(repr(input_file_path)[1:-1], "rb") #Currently done by hardcoded path
    requests.put(signed_url, data=file) #where and what to upload

    data = {
        "input": {
            "files": [signed_url],
            "config": {
                "timestamps_only" : True,
                "export_edits" : True
                }
        }
    }
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    #Ask CleanVoice to do an edit
    response = requests.post("https://api.cleanvoice.ai/v1/edits", json=data, headers=headers)
    temp = response.text
    id = (json.loads(response.text))["id"]
    url = "https://api.cleanvoice.ai/v1/edits/" + id
    headers = {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"

    }

    #Information regarding the edit and its progress
    response = requests.get(url, json = data, headers=headers)
    json_obj= json.loads(response.text)

    #If Editing process is done
    while(json_obj['status'] !=  "SUCCESS" and json_obj['status'] != "FAILURE"):
        response = requests.get(url, json = data, headers=headers)
        json_obj= json.loads(response.text)

    #Gets just a list of the edits 
    edits = json_obj['result']['edits']['edits']
    return(edits)

