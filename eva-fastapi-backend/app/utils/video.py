from .asr import AutoSpeechRecognition
from .audio_assessor import AudioAssessor
from ..features.video_streamliner.streamliner import VideoStreamliner
from ..features.focus_group.focus_group import FocusGroup
from ..features.narration_improver.narration_improver import NarrationImprover
from ..features.narration_improver.narration_improver import NarrationImprover
from .video_trimmer import trim_and_merge_video
import subprocess

## No longer needed. Just left for reference. New version is EVAProject.
class EVA():
    """
    
    """
    def __init__(self):
        """
        """
        self.current_key_clips=[]
        self.cut_manual = False
        self.timestamps = []
        self.transcript = None
        self.audio=None
        return

    def load_media(self,blob_url,local_url,filename):
        """
        
        """
        self.blob_url = blob_url
        self.media_path = local_url

        audio = self.check_audio(file_path=local_url)

        #intialize all the features depending on if theres audio
        self.streamliner = VideoStreamliner(audio)
        self.focus_group = FocusGroup(audio)

        if audio:
            self.narration_improver = NarrationImprover()
            if self.transcript is None:
                self.transcript = self.__generate_transcript(clip_batch_size=0.05)
            self.streamliner.load_media(blob_url,local_url,filename)
        else:
            self.streamliner.load_media(blob_url, local_url, filename)
            self.transcript = None

            self.labels = self.streamliner.streamliner.indexer_result
        
        # load media to features
        self.streamliner.load_media(blob_url,local_url,filename)
        return None
    
    def get_transcript(self):
        """
        Get transcript with timestamps and segment data
        """
        return self.transcript
    def set_transcript(self,transcript):
        """
        Set transcript with timestamps and segment data
        """
        self.transcript = transcript
        return None
    
    def get_audio(self):
        """
        Get audio
        """
        return self.audio
    def set_audio(self,audio):
        """
        Set audio
        """
        self.audio = audio
        return None
    def check_language_is_en(self):
        """
        Check if language is english or not
        """
        # TO DO
        return True
    
    def check_audio(self,file_path):
        """
        If no audio, no need for narration improver and tone,clarity feedback in focus group
        """
        if self.audio is None:
            assessor = AudioAssessor(file_path)

            self.audio= assessor.assess_vid()

        return self.audio

    
    def __generate_transcript(self,clip_batch_size):
        """
        
        """
        if self.check_language_is_en():
            whisper_model = "base.en"
        else:
            whisper_model = "medium"

        speech_recognizer = AutoSpeechRecognition(lib="stable_whisper",model=whisper_model)
        speech_recognizer.load_media(self.media_path,"video")
        transcript_timestamped = speech_recognizer.get_transcript(timestamp=True,clip_duration_percentage=clip_batch_size,minimum_sentence_length=10,max_sentence_length=40)
        
        return transcript_timestamped

    def streamline_video(self):
        """
        Run streamliner
        """
        deleted_clips,self.current_key_clips = self.streamliner.condense_video(transcript=self.transcript)
        return deleted_clips,self.current_key_clips
    
    def improve_narration(self):
        """
        Run narration improver
        """ 
        print("improve_narrator")
        get_edits = self.narration_improver.get_edits(self.media_path)

        return get_edits
    
    def normalize_audio(self):
        """
        Run narration improver
        """ 
        print("normalize_audio")
        get_graph = self.narration_improver.get_audio(self.media_path)

        return get_graph

    def __cut_transcript(self, timestamps):
        filtered_segments = []
        if timestamps is None:
            filtered_segments = self.transcript['segments']
        else:
            for segment in self.transcript['segments']:
                for time_range_index in range(0, len(timestamps)-1):
                    start_time_range, end_time_range = timestamps[time_range_index][0], timestamps[time_range_index][1]
                    if segment['start'] >= start_time_range and segment['end'] <= end_time_range:
                        filtered_segments.append(segment)
                        break
        filtered_transcript = {
            "text": self.transcript['text'],
            "segments": filtered_segments
        }

        return filtered_transcript
    
    def focus_group_run(self, timestamps):
        """
        Run focus group

        """
        #TEST
        if self.audio:
            if len(timestamps) != 0:
                temp_transcript = self.__cut_transcript(timestamps)
                feedback,clip_tones = self.focus_group.run(transcript=temp_transcript)
            else:
                feedback,clip_tones = self.focus_group.run(transcript=self.transcript)
        else: 
            feedback, clip_tones = self.focus_group.run_no_audio(labels=self.labels)       
            
        return feedback,clip_tones

    def trim_merge_important_clips(self,high_scoring_timestamps,output_file_path):
        """
        Merge consecutive important clips
        """
        trim_and_merge_video(input_video=self.media_path, timestamps=high_scoring_timestamps,output_video=output_file_path,audio=self.audio)
        return 
    
    def generate_video(self, current_version_timestamps, output_file_path):
        """
        Generate video based on current timestamps
        """
        print("generate video video.py")
        # print(self.current_key_clips)
        self.timestamps = self.current_key_clips
        print(self.timestamps)
        #if no manual edits are made and if streamliner is already ran...generate video from streamliner result
        if len(current_version_timestamps)<=0:
            print("No current version timetsmps",current_version_timestamps)
            if len(self.current_key_clips)>0:
                current_version_timestamps = self.current_key_clips
                print("keyn timetsmps",current_version_timestamps)
            else:
                #just for simple debugging
                current_version_timestamps = [(0,2)]
        trim_and_merge_video(input_video=self.media_path, timestamps=current_version_timestamps, output_file_path=output_file_path, audio=self.audio)
        return
    
    def normalize_output_media(self,output_file_path,remove_low_rumbling=False):
        """
        Normalize audio
        """
        normalize_command = ["ffmpeg-normalize", str(output_file_path), "-o", str(output_file_path), "-c:a", "aac"]
        print("running normalize command")
        subprocess.run(normalize_command)
        print("normalizing ran fine")
        if remove_low_rumbling:
            remove_rumbling_command = ["ffmpeg-normalize", str(output_file_path), "-prf","highpass=f=100","-o", str(output_file_path), "-c:a", "aac"]
            print("running remove rumbling command")
            subprocess.run(remove_rumbling_command)

        return