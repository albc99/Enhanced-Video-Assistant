import subprocess
import os

"""
File: video_trimmer.py
Description: This file contains the functions to trim and merge videos.
Functionality: This file is used to trim and merge videos.
"""

def trim_video(input_file_path, start, end, output_path='output.mp4', audio=True):
    """
    Trim video from start to end and save to output_path
    """

    command = [
            'ffmpeg',
            '-y',
            '-i', input_file_path,
            '-ss', str(start),
            '-to', str(end),
            output_path
        ]


    print("Cutting from", start, "to", end)
    subprocess.run(command)

def trim_and_merge_video(input_video, timestamps, output_file_path, audio:bool):
    """
    Trim and merge videos
    """
    input_files = []
    concat_file_path = 'concat_file.txt'

    CLIP_LENGTH_TOLERANCE = 0.1

    try:
        print("got to trim and merge")
        # Write a text file listing input files for the concat demuxer
        with open(concat_file_path, 'w') as concat_file:
            for idx, (start_time, end_time) in enumerate(timestamps):
                if abs(end_time - start_time) < CLIP_LENGTH_TOLERANCE:
                    continue

                temp_output_file = f'temp_clip_{idx}.mp4'
                trim_video(input_video, start_time, end_time, temp_output_file, audio)
                input_files.append(temp_output_file)
                concat_file.write(f"file '{temp_output_file}'\n")

        # Concatenate trimmed clips using the concat demuxer
        # Specify -n option in concat demuxer to handle overlapping clips
        concat_command = [
            'ffmpeg',
            '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file_path,
            '-c', 'copy',
            output_file_path
        ]
        subprocess.run(concat_command, capture_output=True)

    except Exception as e:
        print(e)

    finally:
      
        # Clean up temporary files
        for temp_file in input_files:
            # subprocess.run(['rm', temp_file])
            os.remove(temp_file)

        # Clean up concat file
        # subprocess.run(['rm', concat_file_path])
        os.remove(concat_file_path)