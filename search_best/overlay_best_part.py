import dataclasses

from search_best.best_music_part_search import Beat
from search_best.play_of_the_game_search import BestGame


@dataclasses.dataclass
class Snapshot:
    beat_time: float
    video_time: float
    game_position: str


def overlay(beats: list[Beat], game: BestGame, highlight_len: int = 50) -> list[Snapshot]:
    best_beat_index = 0
    best_beat_coolness = -999
    best_game_index = 0
    best_game_points = -999

    if highlight_len > len(beats):
        highlight_len = len(beats)
        for i, beat in enumerate(beats):
            if beat.coolness > best_beat_coolness:
                best_beat_index = i
                best_beat_coolness = beat.coolness
        for i, point in enumerate(game.points[highlight_len:-highlight_len]):
            if point > best_game_points:
                best_game_index = i + highlight_len
                best_game_points = point

        start_beats_index = 0
        end_beats_index = len(beats) - 1
        start_highlight_index = max(0, best_game_index - (highlight_len // 2))
        end_highlight_index = min(len(game.points) - 1, best_game_index + (highlight_len // 2))
    else:
        for i, beat in enumerate(beats[highlight_len:-highlight_len]):
            if beat.coolness > best_beat_coolness:
                best_beat_index = i + highlight_len
                best_beat_coolness = beat.coolness

        for i, point in enumerate(game.points[highlight_len:-highlight_len]):
            if point > best_game_points:
                best_game_index = i + highlight_len
                best_game_points = point

        start_beats_index = max(0, best_beat_index - (highlight_len // 2))
        end_beats_index = min(len(beats) - 1, best_beat_index + (highlight_len // 2))
        start_highlight_index = max(0, best_game_index - (highlight_len // 2))
        end_highlight_index = min(len(game.points) - 1, best_game_index + (highlight_len // 2))

    # if end_highlight_index - start_highlight_index != end_beats_index - start_beats_index:
    #     raise NotImplemented('Хайлайт или дроп где-то скраю, впадлу думать')
    music_start_time = beats[start_beats_index].beat_time
    overlayed_highlight = []
    game_positions = game.game.show_game(start_highlight_index, end_highlight_index)
    for beat_index, highlight_index, game_pos in zip(
        range(start_beats_index, end_beats_index),
        range(start_highlight_index, end_highlight_index),
        game_positions,
    ):
        snapshot = Snapshot(
            beat_time=beats[beat_index].beat_time,
            video_time=beats[beat_index].beat_time - music_start_time,
            game_position=game_pos,
        )
        overlayed_highlight.append(snapshot)
    return overlayed_highlight
