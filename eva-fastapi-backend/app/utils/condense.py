import ffmpeg

def compress_video(input_file, output_file, crf=23):
    (
        ffmpeg
        .input(input_file)
        .output(output_file, crf=crf)
        .overwrite_output()
        .run()
    )
    
