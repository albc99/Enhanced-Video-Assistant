import ffmpeg
import numpy as np
import re

class AutoSpeechRecognition():
    """
    A class for automatic speech recognition using OpenAI's Whisper or SpeechRecognition library.

    Parameters:
    - lib (str): The library to use for speech recognition ("whisper" or "sr").
    - model (str): The model to use for Whisper if lib is "whisper" (e.g., "small","base","tiny" etc).
    Methods:
    - __init__(lib="whisper", model="small"): Initializes the AutoSpeechRecognition instance.
    - load_media(media_path, media_type): Loads the media file for recognition.
    - get_transcript(timestamp=False, clip_duration_percentage=10): Gets the transcript from the loaded media.
    - extract_audio_data(input_video, start_time, end_time, sr=16000): Extracts audio data from a video clip.
    - __get_transcript__whisper(timestamp=False, clip_duration_percentage=10): Internal method for Whisper-based transcription.
    - __get_transcript__sr(): Internal method for SpeechRecognition-based transcription.
    """
    def __init__(self,lib="stable_whisper", model="base.en"):
        """
        Initializes the AutoSpeechRecognition instance.

        Parameters:
        - lib (str): The library to use for speech recognition ("whisper" or "sr").
        - model (str): The model to use for Whisper if lib is "whisper" (e.g., "small").
        """
        self.__lib = lib
        self.__load_lib(lib,model)
    def __load_lib(self,lib,model):
        """
        Load model
        """
        model_path = f"/code/models/{model}.pt"
        if lib=="whisper":
            #OpenAI's whisper
            import whisper
            self.recognizer = whisper.load_model(model_path)

        elif lib=="stable_whisper":
            #Enhanced version of OpenAI's whisper that works very well for this project
            import stable_whisper
            self.recognizer = stable_whisper.load_model(model_path)
            

    def load_media(self,media_path,media_type):
        """
        Loads the media file for recognition.

        Parameters:
        - media_path (str): The path to the media file.
        - media_type (str): The type of media ("video" or "audio").

        Returns:
        None
        """
        ###To DO: ERROR CHECK FOR PATH
        
        self.media_path = media_path
        self.media_type = media_type

        return 
    
    def get_transcript(self, timestamp=False, minimum_sentence_length=15,max_sentence_length=70,clip_duration_percentage=0.1,language="en"):
        """
        Gets the transcript from the loaded media.

        Parameters:
        - timestamp (bool): Whether to include timestamps in the transcript.
        - clip_duration_percentage (float 0-1): Percentage of total duration for each clip in timestamp mode. (only for whisper model)
        - minimum_sentence_length : minimu number of words in sentence/transcript of each clip (only for stable_whsiper version)

        Returns:
        dict: A dictionary containing the transcript information.
        """
        if self.__lib =="whisper":
            transcript = self.__get_transcript__whisper(timestamp, clip_duration_percentage=clip_duration_percentage,language=language)

        elif self.__lib =="stable_whisper":
            transcript = self.__get_transcript_stable_whisper(minimum_sentence_length,max_sentence_length=max_sentence_length,language=language)

        elif self.__lib=="sr":
            transcript = self.__get_transcript__sr()
        return transcript
    
    def extract_audio_data(self, input_video: (str, bytes), start_time, end_time, sr: int = 16000):
        """
        Extracts audio data from a video clip.

        Parameters:
        - input_video (str or bytes): The path to the video file or bytes of the video file.
        - start_time (float): The start time for audio extraction.
        - end_time (float): The end time for audio extraction.
        - sr (int): The sample rate to resample the audio if necessary.

        Returns:
        np.ndarray: A NumPy array containing the audio waveform.
        """
        
        if isinstance(input_video, bytes):
            inp = input_video
            input_video = 'pipe:'
        else:
            inp = None
        
        try:
            # launches a subprocess to decode audio while down-mixing and resampling as necessary.
            out, _ = (
                ffmpeg.input(input_video, ss=start_time, to=end_time)
                .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
                .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=inp)
            )
        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

        return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

    
    def __get_transcript__whisper(self, timestamp=False,clip_duration_percentage=0.1,language="en"):
        """
        Internal method for Whisper-based transcription.

        Parameters:
        - timestamp (bool): Whether to include timestamps in the transcript.
        - clip_duration_percentage (int): Percentage of total duration for each clip in timestamp mode.

        Returns:
        dict or str: A dictionary containing the transcript information or a plain text transcript.
        """
        transcript = {}
        if not timestamp:
            transcript["text"] = self.recognizer.transcribe(self.media_path,language=language)
            return transcript
        else:
            input_video = self.media_path
            
            try:
                # Get video information
                probe = ffmpeg.probe(input_video, v="error", select_streams="a:0")
                total_duration = float(probe["format"]["duration"])
                clip_duration = int(total_duration*clip_duration_percentage)
                
                timestamps = {}
                start_time=0
                end_time = clip_duration
                transcript = " "
                transcript_timestamped = {}
                transcript_timestamped["segments"] = []
                timestamps_lis = []
                #load timestamps
                while end_time <= total_duration:
                    
                    timestamps_lis.append((start_time,end_time))

                    start_time += clip_duration
                    end_time += clip_duration
                timestamps_lis.append((start_time,total_duration))

                # Extract audio from the video clip
                for i,stamps in enumerate(timestamps_lis):
                    audio_data = self.extract_audio_data(input_video, stamps[0], stamps[1])
                    result = self.recognizer.transcribe(audio_data,condition_on_previous_text=transcript,language=language)
                    timestamps[i]=(stamps[0], stamps[1],result)

                    transcript+=result["text"] + " "

                    clip_transcript = {"clip_id":i,"start":stamps[0],"end":stamps[1],"text":result["text"]}

                    transcript_timestamped["segments"].append(clip_transcript)
            except ffmpeg.Error as e:
                print("Error executing ffprobe command:")
                print(e.stderr.decode('utf-8'))
                raise
            transcript_timestamped["text"] = transcript
            return transcript_timestamped


    def __get_transcript_stable_whisper(self,minimum_sentence_length,max_sentence_length,language="en"):
        """
        Generate transcript using stable_whisper's version of OpenAI's Whisper

        Parameter:
         -  minimum_sentence_length : minimu number of words in sentence/transcript of each clip
        """
        import traceback

        transcript = {}
        result = self.recognizer.transcribe(self.media_path,language=language)

        transcript["text"] = result.text
        #get word level timsestamps
        word_lev_ts = result.all_words_or_segments()
        
        try:
            transcript["segments"] = self.__generate_sentence_level_transcript(word_timestamps=word_lev_ts,minimum_sentence_length=minimum_sentence_length,max_sentence_length=max_sentence_length)
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Traceback:")
            traceback.print_exc()
        return transcript

        #word
    
    def __generate_sentence_level_transcript(self,word_timestamps, minimum_sentence_length=10,max_sentence_length=70, skip_punctuations=["Dr.", "Mr.", "Mrs.", "Ms.",'Jr.',"Sr."]):
        """
        Generates sentence level timestamps from a list of word level timestamps.

        Args:
            word_timestamps (list): A list of word level timestamps. Each timestamp is expected to be an object with 'start', 'end', and 'word' attributes.
            minimum_sentence_length (int, optional): The minimum number of words a sentence should have to be included in the output. Defaults to 10.
            max_sentence_length (int, optional): The maximum number of words a sentence can have. Defaults to 70.
            skip_punctuations (list, optional): A list of abbreviations that should not be treated as the end of a sentence. Defaults to ["Dr.", "Mr.", "Mrs.", "Ms.",'Jr.',"Sr."].

        Returns:
            list: A list of sentence level timestamps. Each timestamp is a dictionary with 'start', 'end', and 'text' keys. 'start' and 'end' are the start and end times of the sentence, and 'text' is the sentence text.
        """
        sentences = []
        current_sentence_start = word_timestamps[0].start
        current_sentence_words = []
        
        clip_id = 0
        for i,word_timing in enumerate(word_timestamps):
            current_sentence_words.append(word_timing.word)
            if  len(current_sentence_words)>=max_sentence_length or (word_timing.word.endswith(('.', '!', '?')) and word_timing.word not in skip_punctuations and not re.match("^\d+?\.\d+?$", word_timing.word)):
                if len(current_sentence_words) >= minimum_sentence_length:
                    current_text = ' '.join(current_sentence_words)
                    sentences.append({
                        'clip_id' : clip_id,
                        'start': current_sentence_start,
                        'end': word_timing.end,
                        'text': current_text
                    })
                else:
                    continue
                if word_timing != word_timestamps[-1]:
                    current_sentence_start = word_timestamps[i+1].start
                current_sentence_words = []
                clip_id+=1
        
        if current_sentence_words and len(current_sentence_words) >= minimum_sentence_length:
            sentences.append({
                'clip_id':clip_id,
                'start': current_sentence_start,
                'end': word_timestamps[-1].end,
                'sentence': ' '.join(current_sentence_words)
            })
        
        return sentences

    
    def __get_transcript__sr(self):
        """
        Internal method for SpeechRecognition-based transcription.

        Returns:
        dict: A dictionary containing the transcript information.
        """
        from moviepy.editor import VideoFileClip
        import speech_recognition as sr
        transcript = {}
        # Load video clip
        if media_type==None:
            media_type = self.__get_media_type(self.media_path)
        if media_type=="video":
            video_clip = VideoFileClip(self.media_path)
            # Extract audio from the video
            audio = video_clip.audio.to_soundarray()
            audio_file = video_clip.audio 
        else:
            audio_file = self.media_path
        
        audio_file.write_audiofile("demo.wav")
        # Convert audio data to text using SpeechRecognition
        with sr.AudioFile("demo.wav") as source:
            audio_text = self.recognizer.record(source)
        # Get the transcript with timestamps
        transcript["text"] = self.recognizer.recognize_google(audio_text, show_all=True)
        return transcript
    