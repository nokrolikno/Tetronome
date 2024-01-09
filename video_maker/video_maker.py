import cv2
import glob
from pathlib import Path
import moviepy.editor as mpe
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment


def file_number(filename):
    return int(filename[-9:-4])


def play_frames(frames_dir, fps, output_video_path, music_path):
    # Get the list of frames in the directory
    frames = sorted(glob.glob(str(frames_dir / '*.png')), key=file_number)

    # Read the first frame to get the width and height
    frame = cv2.imread(frames[0])
    height, width, _ = frame.shape

    # Create the video writer object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter('tmp_' + output_video_path, fourcc, fps, (width, height))

    for frame_path in frames:
        # Read the frame
        frame = cv2.imread(frame_path)

        # Write the frame to the video
        video_writer.write(frame)

    # Release the video writer
    video_writer.release()
    AudioSegment.from_wav(music_path).export(music_path[:-4] + '.mp3', format='mp3')
    # loading video dsa gfg intro video
    clip = VideoFileClip('tmp_' + output_video_path, audio=False)

    # loading audio file
    audioclip = AudioFileClip(music_path[:-4] + '.mp3')

    duration = min(clip.duration, audioclip.duration)
    audioclip = audioclip.subclip(0, duration)
    # adding audio to the video clip
    videoclip = clip.set_audio(audioclip)

    videoclip.write_videofile(output_video_path, audio=True)


def create_video(images_path, output_path, fps, music_path):
    # Directory path
    frames_dir = Path(images_path)
    output_video_path = output_path
    output_video_path_mp4 = output_path[:-4] + '.mp4'

    # Play the frames and save as video
    play_frames(frames_dir, fps, output_video_path, music_path)


if __name__ == '__main__':
    create_video('tmp_vid/', 'output.mp4', 44, 'melody_signal.wav')
