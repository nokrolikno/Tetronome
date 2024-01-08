import cv2
import glob
from pathlib import Path
import moviepy.editor as mpe
from pydub import AudioSegment


def file_number(filename):
    return int(filename[-9:-4])


def play_frames(frames_dir, fps, output_video_path):
    # Get the list of frames in the directory
    frames = sorted(glob.glob(str(frames_dir / '*.png')), key=file_number)

    # Read the first frame to get the width and height
    frame = cv2.imread(frames[0])
    height, width, _ = frame.shape

    # Create the video writer object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for frame_path in frames:
        # Read the frame
        frame = cv2.imread(frame_path)

        # Write the frame to the video
        video_writer.write(frame)

    # Release the video writer
    video_writer.release()


# Directory path
frames_dir = Path('./tmp_vid')
music_path = 'melody_signal.wav'
music_path_mp3 = 'melody_signal.mp3'
fps = int(46 * 1.166) * 2
output_video_path = 'vid2output.mp4'

# Play the frames and save as video
play_frames(frames_dir, fps, output_video_path)
AudioSegment.from_wav(music_path).export(music_path_mp3, format="mp3")
audio = mpe.AudioFileClip(music_path_mp3)
video1 = mpe.VideoFileClip(output_video_path)
final = video1.set_audio(audio)
final.write_videofile('output.mp4', codec='mpeg4', audio_codec='libvorbis')
