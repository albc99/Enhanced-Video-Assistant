from .video_condenser import VideoCondenser
from .video_indexer import VideoIndexer
import subprocess
import json
# Base class for video streamliner


"""
File: streamliner.py
Description: This file contains the VideoStreamliner class.
Functionality: This class is used to condense the input video based on the transcript and similarity scores.
"""

class VideoStreamliner():
    """
    
    """
    #might add some parametrs based on if we if we provide an optional user inouts on frontend
    def __init__(self):
        """
        """
        with open('/features/credentials.json', 'r') as file:
            self.data = json.load(file)
        self.condenser = VideoCondenser()
        self.indexer = VideoIndexer(self.data["AZURE_VIDEO_INDEXER_ACCOUNT_ID"], 'trial', self.data["AZURE_VIDEO_INDEXER_API_KEY"])
        return 
    
    def set_audio(self,audio):
        """
        Set audio
        """
        if not audio:
            self.indexer = VideoIndexer(self.data["AZURE_VIDEO_INDEXER_ACCOUNT_ID"], 'trial', self.data["AZURE_VIDEO_INDEXER_API_KEY"])


        self.audio = audio
    
    def get_audio(self):
        """
        Get audio
        """
        return self.audio
    
    def load_media(self, blob_url, local_url, filename,audio, media_type="video"):
        """
        pre-process video and audio files
        """
        if not audio:
            # Double the speed of the video
            sped_up_video_path = f"/code/app/uploads/{filename}_sped_up.mp4"
            subprocess.run(["ffmpeg", "-i", local_url, "-filter:v", "setpts=0.5*PTS", "-c:a", "copy", sped_up_video_path])

            # Call self.streamliner.load_media() with the sped up video
            temp = self.indexer.load_media(sped_up_video_path, blob_url, filename, media_type="video")

            # Delete the sped up video
            subprocess.run(["rm", sped_up_video_path])
        return temp


    async def condense_video(self,transcript=None,media_path=None,indexer_result=None):
        """
        Returns (deleted_clip_timestamps, imported_clip_timestamps, summary)
        """
        if not indexer_result is None:
            high_scored_timestamps,summary = await self.indexer.condense_video(indexer_result=indexer_result)
        else:
            #if it is none, then run the condenser
            high_scored_timestamps,summary = await self.condenser.condense_video(transcript=transcript,media_path=media_path)
        
        deleted_clips = self.__get_deleted_clips_timestamps(high_scored_timestamps)
        # generate a video trimmed based off the high scored timestamps
        print("Condense video worked st.py")
        return deleted_clips,high_scored_timestamps,summary
    
    
    def __get_deleted_clips_timestamps(self,high_scoring_timestamps):
        result = []
        
        if not high_scoring_timestamps:
            return [(0, 'end')]
        
        # Check the gap before the first timestamp
        if int(high_scoring_timestamps[0][0]) != 0:
            result.append((0, high_scoring_timestamps[0][0]))
        
        # Check the gaps between consecutive timestamps
        for i in range(len(high_scoring_timestamps) - 1):
            start = high_scoring_timestamps[i][1]
            end = high_scoring_timestamps[i + 1][0]
            if start!=end:
                result.append((start, end))
        
        # Check the gap after the last timestamp
        result.append((high_scoring_timestamps[-1][1], 'end'))
        
        return result

