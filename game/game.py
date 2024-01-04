from abc import ABC, abstractmethod


class Game(ABC):

    @abstractmethod
    def get_moves(self) -> list[str]:
        pass

    @abstractmethod
    def make_move(self, move: str) -> int:
        pass

    @abstractmethod
    def show_game(self, start: int, end: int) -> list[str]:
        pass
