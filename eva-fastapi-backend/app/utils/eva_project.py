from .asr import AutoSpeechRecognition
from .audio_assessor import AudioAssessor
from ..features.video_streamliner.streamliner import VideoStreamliner
from ..features.focus_group.focus_group import FocusGroup
from ..features.narration_improver.narration_improver import NarrationImprover
from ..database.connect_to_azure_blob import BLOB
from .video_trimmer import trim_and_merge_video
import subprocess
import os
from azure.storage.blob import BlobClient
import whisper
from .translator import translate_text

english_speech_recognizer = AutoSpeechRecognition(model="base.en")
non_english_speech_recognizer = AutoSpeechRecognition(model="medium")
language_detector = whisper.load_model("/code/models/medium.pt")

streamliner = VideoStreamliner()
focus_group = FocusGroup()
narration_improver = NarrationImprover()

DOCKER_FILE_DIRECTORY = "/code/app/uploads/"
BLOB_VIDEO_URL = "https://tsmevastorage.blob.core.windows.net/srceva/"

async def download_video_from_blob(project_id):
    """
    Downloads a video file from Azure Blob Storage if not locally available and saves it to the specified location.

    Args:
        project_id (str): The ID of the project.

    Returns:
        None
    """
    filename = str(project_id) + '.mp4'
    download_path = os.path.join(DOCKER_FILE_DIRECTORY, filename)

    if not os.path.exists(download_path):
        with open(download_path, "wb") as my_blob:
            print("Downloading video to docker")
            connection_string = 'DefaultEndpointsProtocol=https;AccountName=' + 'tsmevastorage' + ';AccountKey=' + 'VcpA6pXx2VKNSSVbgHnbJisOI39bxKDSXCKeLuE' + ';EndpointSuffix=core.windows.net'
            blob_url = BLOB_VIDEO_URL + str(project_id) + '.mp4'
            blob_client = BlobClient.from_blob_url(blob_url, connection_string=connection_string)
            download_stream = blob_client.download_blob()
            my_blob.write(download_stream.readall())
    return

class EVAProject:
    """
    Class to handle the project.

    Attributes:
        project_id (int): The ID of the project.
        media_path (str): The path to the media file associated with the project.
        audio (None): Placeholder for the audio data.
        transcript (None): Placeholder for the transcript data.
    """
    def __init__(self, project_id: int):
        """
        Initializes a new instance of the EvaProject class.

        Args:
            project_id (int): The ID of the project.

        Attributes:
            project_id (int): The ID of the project.
            media_path (str): The path to the media file associated with the project.
            audio (None): Placeholder for the audio data.
            transcript (None): Placeholder for the transcript data.
        """
        self.project_id = project_id
        self.media_path = DOCKER_FILE_DIRECTORY + str(project_id) + ".mp4"
        self.audio = None
        self.transcript = None
        return

    async def load_media(self, local_url, filename, blob_url=None):
        """
        Loads media for the project. Checks if the media has audio and transcribes it if it does.
        If the media does not have audio, runs the indexer on it.
        finally saves the data to the blob storage.

        Args:
            local_url (str): The local URL of the media file.
            filename (str): The filename of the media file.
            blob_url (str, optional): The blob URL of the media file. Defaults to None.

        Returns:
            None
        """
        self.blob_url = blob_url
        self.media_path = local_url
        blob = BLOB()

        #if video not in doecker continer
        await download_video_from_blob(self.project_id)

        project_data = blob.load(self.project_id)

        audio = self.check_audio(file_path=local_url)
        lang = project_data["language"]
        if audio:
            try:
                if lang is None:
                    lang=self.detect_language()
                transcript = self.__generate_transcript(clip_batch_size=0.05,language=lang)
                indexer_result = None
            except Exception as e:
                # something went wrong with transcription most probably because AudioAssesor gave false positive for audio
                # run indexer
                print(e)
                audio = False
                print("except indexer running")
                indexer_result = streamliner.load_media(blob_url, local_url, filename,audio=audio)
                transcript = None
        else:       
            print("indexer running")
            indexer_result = streamliner.load_media(blob_url, local_url, filename,audio=audio)
            transcript = None

        data_dict = {"projectID": self.project_id, "transcript": transcript, "audio": audio,"indexer_result":indexer_result,"language":lang}
        await blob.save(data_dict)
        return
    
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
            audio= assessor.assess_vid()
            return audio

    def detect_language(self):
        """
        Detect language of the video
        """
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(self.media_path)
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(language_detector.device)

        # detect the spoken language
        _, probs = language_detector.detect_language(mel)
        lang = max(probs, key=probs.get)
        print(f"Detected language: {lang}")
        return lang
    
    def __generate_transcript(self, clip_batch_size, language="en"):
        """
        Generate a transcript for the media file. If the language is not English, the transcript is translated to English.

        Args:
            clip_batch_size (float): The percentage of the media file to process at a time.
            language (str, optional): The language of the media file. Defaults to "english".

        Returns:
            list: A list of timestamped transcript segments.

        Raises:
            None

        """
        if str(language).lower() == "english" or str(language).lower() == "en":
            english_speech_recognizer.load_media(self.media_path, "video")
            transcript_timestamped = english_speech_recognizer.get_transcript(
                timestamp=True,
                clip_duration_percentage=clip_batch_size,
                minimum_sentence_length=10,
                max_sentence_length=45,
                language=language,
            )
        else:
            non_english_speech_recognizer.load_media(self.media_path, "video")
            transcript_timestamped = non_english_speech_recognizer.get_transcript(
                timestamp=True,
                clip_duration_percentage=clip_batch_size,
                minimum_sentence_length=15,
                max_sentence_length=45,
                language=language,
            )

            transcript_timestamped = translate_text(
                from_language=language,
                to_language="en",
                transcript_segments_data=transcript_timestamped,
            )
        return transcript_timestamped

    async def streamline_video(self):
        """
        Run streamliner

        This method runs the streamliner to condense the video based on the project data. 
        If the project has audio, it uses the transcript and media path to condense the video. 
        Otherwise, it uses the indexer result from the project data. 
        The condensed video clips are saved and the summary is updated in the project data.

        Returns:
            tuple: A tuple containing the deleted clip timestamps and important clip timestamps.
        """
        blob = BLOB()
        project_data = blob.load(self.project_id)
        #if video not in doecker continer
        await download_video_from_blob(self.project_id)
        if project_data["audio"]:
            deleted_clips,key_clips,summary = await streamliner.condense_video(transcript=project_data["transcript"],media_path=self.media_path)

        else:
            deleted_clips,key_clips,summary = await streamliner.condense_video(indexer_result=project_data["indexer_result"])

        streamliner_data = {"deleted_clip_timestamps": deleted_clips, "important_clip_timestamps": key_clips}
        data_dict = {"projectID":self.project_id, "streamlinerData":streamliner_data,"summary":summary}
        await blob.save(data_dict)

        return deleted_clips,key_clips
    
    async def improve_narration(self):
        """
        Run narration improver.

        Downloads the video from the blob storage, applies edits to improve the narration,
        saves the edited data to the blob storage, and returns the edits made.

        Returns:
            list: The edits made to improve the narration.
        """ 
        blob = BLOB()
        #if video not in doecker continer
        await download_video_from_blob(self.project_id)
        edits = narration_improver.get_edits(self.media_path)
        narration_data = {"edits":edits}
        data_dict = {"projectID":self.project_id, "narrationImproverData":narration_data}
        await blob.save(data_dict)
        return edits
    
    def __cut_transcript(self, timestamps,transcript):
        """
        Cuts the transcript based on manual edits specified by timestamps.

        Args:
            timestamps (list): A list of start and end timestamps indicating the time ranges to keep in the transcript.
            transcript (dict): The original transcript containing the text and segments.

        Returns:
            dict: The filtered transcript with only the segments within the specified time ranges.
        """
        filtered_segments = []
        ## this is not called as of rn, but will be used to cut the transcript based on manual edits
        ## if list is empty, we can assume that no manual edits were made and we can use the original transcript
        if timestamps is None:
            flitered_segments = transcript['segments']
        else:
            for segment in self.transcript['segments']:
                for time_range_index in range(0, len(timestamps)-1, 2):
                    start_time_range, end_time_range = timestamps[time_range_index],timestamps[time_range_index+1]
                    if segment['start'] >= start_time_range and segment['end'] <= end_time_range:
                        filtered_segments.append(segment)
                        break  # Move to the next segment if this segment is within a time range

        # Update the original transcript with the filtered segments
        filtered_transcript = {
            "text": transcript['text'],
            "segments": filtered_segments
        }

        return filtered_transcript

    async def focus_group_run(self, timestamps):
        """
        Run focus group.

        This method runs the focus group analysis on the project's transcript data.
        If the project has audio, it extracts the transcript and performs the focus group analysis.
        If timestamps are provided, it cuts the transcript based on the given timestamps before running the analysis.
        If the project does not have audio, it uses the indexer results to perform the analysis.

        :param timestamps: A list of timestamps to cut the transcript (optional)
        :type timestamps: list

        :return: A tuple containing the feedback, clip tones, and tone feedback
        :rtype: tuple
        """
        blob = BLOB()
        project_data = blob.load(self.project_id)
        if project_data["audio"]:
            transcript = project_data["transcript"]
            if timestamps is not None and len(timestamps) != 0:
                temp_transcript = self.__cut_transcript(timestamps,transcript=transcript)
                feedback, clip_tones, tone_feedback = focus_group.run(transcript=temp_transcript)
            else:
                feedback, clip_tones, tone_feedback = focus_group.run(transcript=transcript)
        else: 
            print("indexer fg")
            indexer_results = project_data["indexer_result"]
            feedback, clip_tones, tone_feedback= focus_group.run_no_audio(labels=indexer_results)

        fg_data = {"feedback": feedback, "clip_tones": clip_tones, "tone_feedback": tone_feedback}
        data_dict = {"projectID":self.project_id, "focusGroupData":fg_data}
        await blob.save(data_dict)
        return feedback, clip_tones, tone_feedback

    def focus_group_chat(self, query):
        """
        Run focus group chat.

        This method runs a focus group chat for the project. It loads the project data from the BLOB storage,
        checks if the project has a summary, and then calls the `focus_group_chat` function from the `focus_group`
        module to perform the chat. If the project doesn't have a summary, it returns a message indicating that
        the process can't be completed for the video.

        Args:
            query (str): The query for the focus group chat.

        Returns:
            str: The response from the focus group chat.
        """
        blob = BLOB()
        project_data = blob.load(self.project_id)
        if project_data["summary"]:
            chat_response = focus_group.focus_group_chat(query, project_data)
        else:
            chat_response = "Sorry, the process can't be completed for this video."
        return chat_response
    
    def trim_merge_important_clips(self, high_scoring_timestamps, output_file_path):
        """
        Trim and merge consecutive important clips.

        Args:
            high_scoring_timestamps (list): List of high scoring timestamps.
            output_file_path (str): Path to the output video file.

        Returns:
            None
        """
        trim_and_merge_video(input_video=self.media_path, timestamps=high_scoring_timestamps, output_video=output_file_path, audio=self.audio)
        return
    
    async def generate_video(self,current_version_timestamps,output_file_path):
        """
        Generate video based on current timestamps.

        Args:
            current_version_timestamps (list): List of timestamps for the current version.
            output_file_path (str): Path to save the generated video.

        Returns:
            None
        """
        #if video not in doecker continer
        await download_video_from_blob(self.project_id)

        blob = BLOB()
        project_data = blob.load(self.project_id)
        streamliner_timestamps = project_data["streamlinerData"]["important_clip_timestamps"]
        audio = project_data["audio"]
        #if no manual edits are made and if streamliner is already ran...generate video from streamliner result
        if current_version_timestamps and len(current_version_timestamps)<=0:
            print("No current version timetsmps",current_version_timestamps)
            if len(streamliner_timestamps)>0:
                current_version_timestamps = streamliner_timestamps
                print("keyn timetsmps",current_version_timestamps)
            else:
                #just for simple debugging
                current_version_timestamps = [(0,2)]
        trim_and_merge_video(input_video=self.media_path, timestamps=current_version_timestamps,output_file_path=output_file_path,audio=audio)
        return

    async def normalize_output_media(self,output_file_path,remove_low_rumbling=False):
        """
        Normalize audio.

        Args:
            output_file_path (str): The path of the output file to be normalized.
            remove_low_rumbling (bool, optional): Whether to remove low rumbling noise. Defaults to False.
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
