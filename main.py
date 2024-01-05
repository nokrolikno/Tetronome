from os import listdir
from os.path import isfile, join
import time

from ThreeInRow.ThreeInRow import ThreeInRow
from search_best.best_music_part_search import MusicSearcher
from search_best.overlay_best_part import overlay
from search_best.play_of_the_game_search import HighlightSearcher
import sounddevice as sd


def pipeline(source):
    music_searcher = MusicSearcher(source)
    beats = music_searcher.define_best_parts(normalize=True)
    highlight_searcher = HighlightSearcher(ThreeInRow, len(beats))
    best_score_game, best_combo_game = highlight_searcher.search()
    snapshots = overlay(beats, best_score_game, highlight_len=50)
    print(snapshots)
    best_part_music_data = music_searcher.y[int(snapshots[0].beat_time * music_searcher.sr):int(
        snapshots[-1].beat_time * music_searcher.sr)]
    sd.play(best_part_music_data, music_searcher.sr)
    start = time.time()
    for snapshot in snapshots:
        while True:
            if time.time() - start > snapshot.video_time:
                print(snapshot.game_position)
                break
            time.sleep(1e-6)


def main():
    mypath = input('source: ')
    pipeline(mypath)


if __name__ == '__main__':
    main()
