import requests
import time
from collections import defaultdict
from datetime import datetime
from math import ceil
import os

"""
File: video_indexer.py
Description: This file contains the VideoIndexer class.
Functionality: This class is used to interact with the Azure Video Indexer API.
"""

class VideoIndexer():
    """
    
    """

    def __init__(self, account_id, location, api_key, api_url = "https://api.videoindexer.ai") -> None:
        """
        get account id from video indexer portal
        get key from here https://api-portal.videoindexer.ai/profile
        location is "trail" if its a trial account
        """
        self.api_url = api_url
        self.account_id = account_id
        self.api_key = api_key
        self.location = location
        self.__get_account_access_token()
        return 

    def __get_account_access_token(self):
        """
        Get account access token
        """
        # create the http session
        self.session = requests.Session()
        self.session.headers["Ocp-Apim-Subscription-Key"] = self.api_key
        
        # obtain account access token
        self.__account_access_token = self.session.get(f"{self.api_url}/auth/{self.location}/Accounts/{self.account_id}/AccessToken?allowEdit=true").text.strip('"')
        self.session.headers.pop("Ocp-Apim-Subscription-Key")

        return
    
    def load_media(self,local_url,blob_url,filename,media_type=None)->None:
        """
        Load media to streamliner:indexer

        run complete indexer here and return results
        """
        self.blob_url = blob_url
        self.media_path = local_url
        self.__upload_media_to_indexer(local_url,filename)

        video_access_token = self.__get_video_access_token()
        indexer_result = self.__get_indexer_results(video_access_token=video_access_token)
        return indexer_result
    
    def __upload_media_to_indexer(self, local_url, filename: str) -> None:
        # Get the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Extract the file extension
        _, file_extension = os.path.splitext(filename)

        # Append timestamp to the filename to ensure uniqueness
        unique_filename = f"{filename}_{timestamp}{file_extension}"

        # Open the file for uploading
        with open(local_url, 'rb') as file:
            files = {'file': (unique_filename, file, 'video/mp4')}  # Assuming the video file format is mp4
            upload_response = self.session.post(f"{self.api_url}/{self.location}/Accounts/{self.account_id}/Videos?accessToken={self.__account_access_token}&name={unique_filename}&privacy=public", files=files)

        upload_result = upload_response.json()
        
        self.__video_id = upload_result["id"]
        return
    
    def __get_video_access_token(self):
        """
        Get video access token for the uploaded video to get indexer results
        """
        self.session.headers["Ocp-Apim-Subscription-Key"] = self.api_key
        video_access_token = self.session.get(f"{self.api_url}/Auth/{self.location}/Accounts/{self.account_id}/Videos/{self.__video_id}/AccessToken?allowEdit=true").text.strip('"')
        return video_access_token
    
    def __get_indexer_results(self,video_access_token):
        """
        Get results from video indexer
        """
        states = []
        while True:
            time.sleep(10)
            video_get_index_response = self.session.get(f"{self.api_url}/{self.location}/Accounts/{self.account_id}/Videos/{self.__video_id}/Index?accessToken={video_access_token}&includedInsights")
            video_get_index_result = video_get_index_response.json()
            processing_state = video_get_index_result["state"]
            states.append(processing_state)
            print(f"State: {processing_state}")
            # job is finished
            if processing_state != "Uploaded" and processing_state != "Processing":
                return video_get_index_result
            elif states == ["OK", "Explicit", "Removed", "None"]:
                print("Moderation test failed: Sensitive content detected")

    def timestamp_to_seconds(self,timestamp):
        '''
        Turns timestamp strings to seconds (float)
        returns: float (seconds in input timestamp)
        '''
        h, m, s = map(float, timestamp.split(':'))
        return h * 3600 + m * 60 + s

    def __get_timestamps(self, video_index_result)->list:
        """
        Read the response from azure video indexer.
        Get required timestamps of key moments
        """
        vid_duration_sec = video_index_result['videos'][0]['insights']['duration']

        label_timestamps = defaultdict(list)
        scene_timestamps = defaultdict(list)

        for insight in video_index_result['videos'][0]['insights']['labels']:
            label_name = insight['name']
            for instance in insight['instances']:
                timestamp = (self.timestamp_to_seconds(instance['start']), self.timestamp_to_seconds(instance['end']))
                label_timestamps[label_name].append(timestamp)

        for scene in video_index_result['videos'][0]['insights']['scenes']:
            scene_id = scene['id']
            for instance in scene['instances']:
                timestamp = (self.timestamp_to_seconds(instance['start']), self.timestamp_to_seconds(instance['end']))
                scene_timestamps[scene_id].append(timestamp)


        scene_label_overlap_counts = defaultdict(int)

        for scene_id, scene_ranges in scene_timestamps.items():
            for scene_start, scene_end in scene_ranges:
                for label_ranges in label_timestamps.values():
                    for label_start, label_end in label_ranges:
                        if not (scene_end < label_start or label_end < scene_start):
                            scene_label_overlap_counts[scene_id] += 1
                            break

        sorted_scenes = sorted(scene_label_overlap_counts.keys(), key=lambda x: scene_label_overlap_counts[x], reverse=True)

        temp = []

        for scene in sorted_scenes:
            timestamp_ranges = scene_timestamps[scene]
            timestamp_ranges_in_seconds = [(end - start) for start, end in timestamp_ranges]
            temp.append([scene, scene_label_overlap_counts[scene], timestamp_ranges_in_seconds])

        for i in temp:
            i[2] = i[2][0]

        # Goal length set to 1/4 of original video length
        curr_result_len = 0
        goal_len = self.timestamp_to_seconds(vid_duration_sec) / 4
        segment_len = goal_len / 3  # Define segment length as a third of the goal length
        most_labeled = []

        for scene in temp:
            scene_id, _, scene_duration = scene
            if curr_result_len < goal_len:
                if scene_duration > segment_len:
                    # Calculate the number of segments needed
                    num_segments = int(ceil(scene_duration / segment_len))

                    full_scene_start, full_scene_end = scene_timestamps[scene_id][0]
                    full_scene_duration = full_scene_end - full_scene_start

                    segment_duration = full_scene_duration / num_segments
                    
                    # Create and add each segment
                    for segment in range(num_segments):
                        start_time = full_scene_start + segment * segment_duration
                        end_time = min(start_time + segment_duration, full_scene_end)
                        
                        if curr_result_len + (end_time - start_time) <= goal_len:
                            most_labeled.append([scene_id, 1, end_time - start_time])
                            curr_result_len += end_time - start_time
                else:
                    most_labeled.append(scene)
                    curr_result_len += scene_duration
            else:
                break

        result = []
        for scene in video_index_result['videos'][0]['insights']['scenes']:
            for labeled_scene in most_labeled:
                if scene['id'] == labeled_scene[0]:
                    new_timestamp = (scene_timestamps[scene['id']][0][0], scene_timestamps[scene['id']][0][1])
                    # Prevent adding duplicates by checking if the timestamp is already in the result
                    if new_timestamp not in result:
                        result.append(new_timestamp)
        
        return result

    async def condense_video(self,indexer_result):
        """
        Return a list of high scoring transcripts
        """

        #Step 3 : Extract timestamps from indexer response
        high_scored_timestamps = self.__get_timestamps(video_index_result=indexer_result)

        #TO DO get some kind of video summary from labels generated
        summary = "TO DO get some kind of video summary from labels generated from indexer"
        return high_scored_timestamps,summary
