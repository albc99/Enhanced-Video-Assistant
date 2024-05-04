from .clean_voice_api import get_narration_edits
from .audio import Audio
from pydub import AudioSegment

"""
File: narration_improver.py
Description: This file contains the NarrationImprover class.
Functionality: This class is used to interact with the CleanVoice API to improve the narration of the video.
"""

class NarrationImprover():
    """
    """
    def __init__(self) -> None:
        pass

    def get_edits(self,input_file_path):
        return get_narration_edits(input_file_path)
    

