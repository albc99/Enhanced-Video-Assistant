import numpy as np
import subprocess
import ffmpeg
import pyloudnorm as pyln
import matplotlib.pyplot as plt

#https://github.com/csteinmetz1/pyloudnorm
class Audio:
    """
    Generalized class for audio files
    """
    def __init__(self):
        self.pipe = None
        self.speech_recognizer = None
        return
    

    def extract_audio_data(self,input_video: (str, bytes)):
        """
        Extracts audio data from a video clip.

        Parameters:
        - input_video (str or bytes): The path to the video file or bytes of the video file.

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
                ffmpeg.input(input_video)
                .output("-", format="s16le", acodec="pcm_s16le", ac=1)
                .run(cmd="ffmpeg", capture_stdout=True, capture_stderr=True, input=inp)
            )
        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

        return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

        
    def read(self, video_path):
        """
        Reads audio data from a video file using ffprobe.

        Parameters:
        - video_path (str): The path to the video file.

        Returns:
        tuple: A tuple containing the audio waveform (np.ndarray) and its sample rate (int).
        """
        # Get the sample rate of the video using ffprobe
        sample_rate = subprocess.check_output(
            ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=sample_rate', '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            text=True
        )
        self.media_path = video_path
        self.sample_rate = int(sample_rate.strip())
        self.audio_data = self.extract_audio_data(video_path)
        return self.audio_data, self.sample_rate
    

    def __get_loudness(self, data, rate):
        """
        Calculates the integrated loudness of the audio data.

        Parameters:
        - data (np.ndarray): The audio waveform.
        - rate (int): The sample rate of the audio data.

        Returns:
        float: The integrated loudness value.
        """
        meter = pyln.Meter(rate)  # create BS.1770 meter
        loudness = meter.integrated_loudness(data)  # measure loudness
        return loudness

    def peak_normalized(self, filename, lufs_val=-1.0):
        """
        Applies peak normalization to the audio data.
        refer to: https://en.wikipedia.org/wiki/Audio_normalization

        Parameters:
        - filename (str): The path to the video file.
        - lufs_val (float): The target loudness level for peak normalization

        Returns:
        np.ndarray: Peak-normalized audio data.
        rate 
        """
        data, rate = self.read(filename)
        # peak normalize audio to -1 dB
        peak_normalized_audio = pyln.normalize.peak(data, lufs_val)
        return peak_normalized_audio,rate

    def loudness_normalized(self, filename, lufs_val=-14.0):
        """
        Applies loudness normalization to the audio data.
        refer to: https://en.wikipedia.org/wiki/Audio_normalization

        streaming and music platforms use this with a standard lufs val of -14
        Parameters:
        - filename (str): The path to the video file.
        - lufs_val (float): The target loudness level for loudness normalization

        Returns:
        np.ndarray: Loudness-normalized audio data.
        """
        data, rate = self.read(filename)

        loudness = self.__get_loudness(data, rate)

        # loudness normalize audio to -14 dB LUFS 
        loudness_normalized_audio = pyln.normalize.loudness(data, loudness, lufs_val)

        return loudness_normalized_audio,rate
    
    def analyze_sentiments(self,plot=True):
        """
        """
        #load models is not already
        if self.pipe==None:
            from transformers import pipeline
            self.pipe = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        
        if self.speech_recognizer==None:
            from asr import AutoSpeechRecognition
            self.speech_recognizer = AutoSpeechRecognition(lib="whisper",model='tiny.en')

        #get timestamped transcripts
        self.speech_recognizer.load_media(media_path=self.media_path,media_type="video")
        transcript_timestamped = self.speech_recognizer.get_transcript(timestamp=True,clip_duration_percentage=0.05)
        text_values = [segment['text'] for segment in transcript_timestamped['segments']]

        #get sentiment scores for each clip
        sentiment_scores = self.pipe(text_values)
        for i,segment in enumerate(transcript_timestamped["segments"]):
            segment["sentiment_label"] = sentiment_scores[i]["label"]
            segment["sentiment_score"] = sentiment_scores[i]["score"]
        return transcript_timestamped
  

    def normalize_audio(self,input_file, type="loudness"):
        """
        
        """
        if type=="peak":
            normalized_audio, rate = self.peak_normalized(input_file)

        else:
            normalized_audio, rate = self.loudness_normalized(input_file)

            # Ensure the normalized_audio array is in int16 format
        if normalized_audio.dtype != np.int16:
            normalized_audio = normalized_audio.astype(np.int16)

        # Ensure the normalized_audio array is in little endian byte order
        if normalized_audio.dtype.byteorder != '<':
            normalized_audio = normalized_audio.byteswap().newbyteorder()

        # Use ffmpeg to replace audio in the video file with the normalized audio
        command = ['ffmpeg', '-i', input_file, '-i', '-', '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0', '-y', input_file]
        subprocess.run(command, input=normalized_audio.tobytes(), check=True)

        return 

    def plot_audio_waveform(audio_data, sample_rate):
        duration = len(audio_data) / sample_rate
        time_axis = np.linspace(0, duration, len(audio_data))

        plt.figure(figsize=(5, 3))
        plt.plot(time_axis, audio_data, color='blue')
        plt.title('Audio Waveform')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Amplitude')
        plt.grid(True)
        plt.show()
