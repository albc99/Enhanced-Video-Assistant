from .summarizer.summarize import T5Summarizer
from .text_comparision.text_similarity import TextComparer
import subprocess
import numpy as np

"""
File: video_condenser.py
Description: This file contains the VideoCondenser class.
Functionality: This file is used to condense the input video based on the transcript and similarity scores.
"""

class VideoCondenser():
    """
    
    """
    def __init__(self,language="english"):
        
        self.summarizer = T5Summarizer(model="t5-base" )
        self.comparer = TextComparer(language=language,method="model")
        self.min_duration = 0
        self.max_duration = 0
        return
    
    def load_media(self,local_url,blob_url=None,filename=None, media_type = "video"):
        """
        """
        self.media_path = local_url
        return
        
    
    def get_number_of_clips(self):
        """
        
        """
        return
    
    def set_minimum_output_duration(self, duration):
        """
        Set the minimum output duration.

        Parameters:
        - duration: float, either a percent value (0.00-1.00) or a duration value in seconds
        """

        if 0 <= duration <= 1.0:  # Assume duration is a percent value
            self.min_duration = duration * self.media_duration
        elif duration >= 0:  # Assume duration is in seconds
            self.min_duration = duration
        else:
            raise ValueError("Invalid duration value. Should be either a percent value (0.00-1.00) or a duration value in seconds.")


    def set_maximum_output_duration(self,duration):
        """
        Set the max output duration.

        Parameters:
        - duration: float, either a percent value (0.00-1.00) or a duration value in seconds
        """

        if 0 <= duration <= 1.0:  # Assume duration is a percent value
            self.max_duration = duration * self.media_duration
        elif duration >= 0:  # Assume duration is in seconds
            self.max_duration = duration
        else:
            raise ValueError("Invalid max duration value. Should be either a percent value (0.00-1.00) or a duration value in seconds.")


    def __get_video_duration(self,media_path):
        """
        """
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", media_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
        return float(result.stdout)
    
    def get_intro(self):
        """
        get an intro from input video which can be appended to start of our output vid for better flow of context        
        """

        return
    
    def get_outro(self):
        """
        get an outro from input video which can be appended to end of our output vid for better flow of context
        """

        return
    async def condense_video(self,transcript,media_path,clip_batch_size = 0.05):
        """
        clip_batch_size, float 0-1: the video is processed as a set of clips each of duration 5% of total duration. small values (0.00-0.2) are optimal

        Returns a list of highscoring timestamps and transcript summary
        """
        # self.media_duration = self.__get_video_duration(media_path)
        # if self.min_duration==0:
        #     self.set_minimum_output_duration(0.2)
        # if self.max_duration==0:
        #     self.set_maximum_output_duration(0.75)
        # self.num_clips = int(1/clip_batch_size)
        print("Indexing might take a while especially if video is longer...")

        # Step 2: generate summary of transcript
        summary = self.summarizer.summarize(transcript["text"], max_input_length=700)

        #step 3: generate similarity scores and time stamp's list
        self.comparer.set_superior_text(summary)
        segment_similarity_scores, time_stamp_list= self.__process_comparision(transcript["segments"])

        #step 4: get the timestamps of high scored clips 
        high_scored_timestamps = self.__get_best_clip_timestamps(segment_similarity_scores, time_stamp_list)
           
        
        return self.merge_intervals(high_scored_timestamps),summary
    

    def merge_intervals(self,intervals):
        """
        Merge consecutive intervals
        """
        if not intervals:
            return []
        
        merged = []
        start, end = intervals[0]
        
        for i in range(1, len(intervals)):
            if intervals[i][0] <= end:
                # if it does, then merge the current and last interval in merged list
                end = max(end, intervals[i][1])
            else:
                # if it doesn't overlap, add it to the result
                merged.append((start, end))
                start, end = intervals[i]

        # Add the last interval
        merged.append((start, end))

        return merged
    def __process_comparision(self, segments):
        """
        """
        step_size = max(2,int(0.05*len(segments)))
        segment_similarity_scores = []
        time_stamp_list = []
        for i in range(0, len(segments) - step_size, step_size):
            score = self.comparer.get_similarity_score(segments[i]["text"] + segments[i + step_size]["text"])
            start_time = segments[i]["start"]
            end_time = segments[i + step_size]["end"]
            time_stamp_list.append((start_time, end_time))
            segment_similarity_scores.append(score)

        # Process remaining segments if there are any
        if len(segments) % step_size != 0:
            i = len(segments) - step_size
            score = self.comparer.get_similarity_score(segments[i]["text"] + segments[-1]["text"])
            start_time = segments[i]["start"]
            end_time = segments[-1]["end"]
            time_stamp_list.append((start_time, end_time))
            segment_similarity_scores.append(score)

        return segment_similarity_scores, time_stamp_list

    #sort time_stamp_list based on descending ordered similarity scores
    def __get_best_clip_timestamps(self, similarity_scores, time_stamps_list):
        """
        
        """
        if not similarity_scores or not time_stamps_list:
            return None

        min_clips = int(0.25*len(similarity_scores))
        max_clips = int(0.60*len(similarity_scores))
        # Get the optimal number of clips within the specified range
        optimal_num_clips = max(min_clips, min(max_clips, sum(1 for score in similarity_scores if score>0)))

        # Get the highest scoring segments
        indices = np.argsort(similarity_scores)[::-1]
        
        ordered_top_indices = np.sort(indices[0:optimal_num_clips])
        # Get the timestamps of the top @optimal_num_clips timestamps

        selected_time_stamps = []
        for clip_index in ordered_top_indices:
            selected_time_stamps.append(time_stamps_list[clip_index])

        return selected_time_stamps
    


