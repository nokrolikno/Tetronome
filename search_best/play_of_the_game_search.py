from __future__ import annotations

import dataclasses
import random
from typing import Type
from game.game import Game
from search_best.best_music_part_search import SlidingWindowMixin


@dataclasses.dataclass
class BestGame:
    game: Game | None
    points: list[int]


class PrimitiveGame(Game):
    def get_moves(self) -> list[str]:
        pass

    def make_move(self, move: str) -> int:
        pass

    def show_game(self, start: int, end: int) -> list[str]:
        pass


class HighlightSearcher(SlidingWindowMixin):
    def __init__(self, game: Type[Game], n_beats: int, highlight_len: int = 10):
        self.game = game
        self.n_beats = n_beats
        self.highlight_len = highlight_len

    def simulate(self, game: Game) -> list[int]:
        moves = game.get_moves()
        points = []
        for i in range(self.n_beats):
            points.append(game.make_move(random.choice(moves)))
            moves = game.get_moves()
        return points

    def search(self, play_games: int = 10) -> tuple[BestGame, BestGame]:
        most_scores = -999
        most_scored_game = BestGame(None, [-999])
        most_combo_score = -999
        most_combo_game = BestGame(None, [-999])
        for i in range(play_games):
            game = self.game()
            points = self.simulate(game)
            if max(points) > most_scores:
                most_scored_game = BestGame(game, points)
                most_scores = max(points)
            for windowed_points in self.sliding_window(points, self.highlight_len):
                if sum(windowed_points) > most_combo_score:
                    most_combo_game = BestGame(game, points)
                    most_combo_score = sum(windowed_points)
        return most_scored_game, most_combo_game
