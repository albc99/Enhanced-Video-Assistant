import numpy as np
import subprocess
import ffmpeg
import pyloudnorm as pyln
# import matplotlib.pyplot as plt

class Audio:
    """
    Generalized class for audio files
    """
    def __init__(self):
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
        sample_rate = int(sample_rate.strip())
        audio_data = self.extract_audio_data(video_path)
        return audio_data, sample_rate
    

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
        """
        data, rate = self.read(filename)
        # peak normalize audio to -1 dB
        peak_normalized_audio = pyln.normalize.peak(data, lufs_val)
        return peak_normalized_audio

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

        return loudness_normalized_audio
    

    def normalization():
        return 4
    # def plot_audio_waveform(audio_data, sample_rate):
    #     duration = len(audio_data) / sample_rate
    #     time_axis = np.linspace(0, duration, len(audio_data))

    #     plt.figure(figsize=(5, 3))
    #     plt.plot(time_axis, audio_data, color='blue')
    #     plt.title('Audio Waveform')
    #     plt.xlabel('Time (seconds)')
    #     plt.ylabel('Amplitude')
    #     plt.grid(True)
    #     # plt.show()
    #     plt.savefig("/Users/cse498/Desktop/graph.png", format='png')
    #     plt.close()