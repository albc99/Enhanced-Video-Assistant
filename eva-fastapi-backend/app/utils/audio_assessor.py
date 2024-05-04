import subprocess
import json
from pydub import AudioSegment
from pydub.silence import detect_nonsilent


"""
File: audio_assessor.py
Description: This file contains the AudioAssessor class.
Functionality: This class is used to assess the audio of a video.
"""


class AudioAssessor():

    def __init__(self, file_path):
        self.vid_path = file_path

    def _has_audio(self):
        '''
        Run FFmpeg for metadata of video, parse the output as JSON, then check for audio stream in its streams
        return: bool if video has audio or not
        '''
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", self.vid_path]
        result = subprocess.run(cmd, capture_output=True, check=True)
        streams = json.loads(result.stdout)['streams']
        
        return any(stream['codec_type'] == 'audio' for stream in streams)
    
    def _check_transcribable(self):
        '''
        Run FFmpeg for audio extraction, check if audio is transcribable with loudness test and silence rate 
        test.
        return: bool if audio is transcribable or not
        '''

        # parameters set for ffmpeg: ignore video, audio rate, single channel audio, output format, pipe
        cmd = ["ffmpeg", "-i", self.vid_path, "-vn", "-ar", "16000", "-ac", "1", "-f", "wav", "-"]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        audio_data = AudioSegment(data=result.stdout)

        # loudness obtained as audio's decibel relative to full scale
        loudness = audio_data.dBFS

        nonsilent_seg = detect_nonsilent(audio_data, min_silence_len=1000, silence_thresh=-40)
        total_duration = len(audio_data)
        nonsilent_duration = sum([end - start for start, end in nonsilent_seg])
        silence_percentage = 100 - (nonsilent_duration / total_duration * 100)

        if loudness <= -10.0 and silence_percentage > 0:
            # When loudness and silence rate tests are passed, voice recognition algorithm ensures
            # that the audio has sufficient amount of transcribable audio. However, as this process takes
            # a long time, we might delete. 
            # recognizer = sr.Recognizer()
            # with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp_file:
            #     tmp_file.write(result.stdout)
            #     tmp_file.flush()
            #     with sr.AudioFile(tmp_file.name) as source:
            #         audio_sample = recognizer.record(source)

            #     try:
            #         text = recognizer.recognize_google(audio_sample)
            #         if text:
            #             return True
            #     except sr.UnknownValueError:
            #         # Speech was unintelligible
            #         pass
            return True

        return False


    def assess_vid(self):
        '''
        Checks if a video has audio or not, and if it does, if the audio is transcribable or not.
        prints what process to be done after with the returned result.
        returns: bool if audio is transcribable
        '''
        if self._has_audio():
            if self._check_transcribable():
                '''
                Run Video Condensor
                '''
                print("Video has transcribable audio streams. Proceed with video condensor")
                return True

            else:
                '''
                Run Video_indexer
                '''
                print("Video does not have transcribable audio streams. Proceed with video indexer")
                return False

        else:
            '''
            Run Video Indexer
            '''
            print("Video does not have audio streams. Proceed with video indexer")
            return False