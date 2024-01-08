import time
import numpy as np
from scipy.io import wavfile

from ThreeInRow.ThreeInRow import ThreeInRow
from search_best.best_music_part_search import MusicSearcher
from search_best.overlay_best_part import overlay
from search_best.play_of_the_game_search import HighlightSearcher
import sounddevice as sd


def pipeline(source):
    music_searcher = MusicSearcher(source)
    beats = music_searcher.define_best_parts(normalize=True)
    highlight_searcher = HighlightSearcher(ThreeInRow, 1000)
    best_score_game, best_combo_game = highlight_searcher.search()
    snapshots = overlay(beats, best_score_game, highlight_len=50)
    print(f'BPM = {music_searcher.bpm}')
    best_part_music_data = music_searcher.y[
        int(snapshots[0].beat_time * music_searcher.sr) : int(snapshots[-1].beat_time * music_searcher.sr)
    ]
    with open('./ThreeInRow/output.txt', 'w') as file:
        for snapshot in snapshots:
            file.write(snapshot.game_position + '\n')
    scaled = np.int16(best_part_music_data / np.max(np.abs(best_part_music_data)) * 32767)
    wavfile.write('ThreeInRow/melody_signal.wav', 44100, scaled)
    # sd.play(best_part_music_data, music_searcher.sr)
    # start = time.time()
    # for snapshot in snapshots:
    #     while True:
    #         if time.time() - start > snapshot.video_time:
    #             print(snapshot.game_position)
    #             break
    #         time.sleep(1e-6)


def main():
    mypath = input('source: ')
    pipeline(mypath)


if __name__ == '__main__':
    main()
