import random
import time

from game.game import Game

ROWS_NUM = 10
COLS_NUM = 10  # TODO: ряди и колонки наоборот
GEM_SIZE = 60
WIN_RES = WIN_W, WIN_H = ROWS_NUM * GEM_SIZE, COLS_NUM * GEM_SIZE
COLORS = ["red", "green", "blue"]


class ThreeInRow(Game):
    # 1) Create board w/o 3+ in a row
    def __init__(self):
        self.is_exploding = False
        self.is_falling = False
        self.remove_cells = []
        self.gameState_string = ""
        self.GameState = []
        # create full random board which will be fully overridden, not empty just for warning evasion
        self.board = [
            [Gem(i, j, random.choice(COLORS)) for i in range(COLS_NUM)]
            for j in range(ROWS_NUM)
        ]
        for y in range(COLS_NUM):
            for x in range(ROWS_NUM):
                good_colors = COLORS.copy()
                if y - 2 >= 0:
                    if self.board[y - 1][x].color == self.board[y - 2][x].color:
                        good_colors.remove(self.board[y - 2][x].color)
                if x - 2 >= 0:
                    if self.board[y][x - 1].color == self.board[y][x - 2].color:
                        if self.board[y][x - 2].color in good_colors:
                            good_colors.remove(self.board[y][x - 2].color)
                self.board[y][x] = Gem(y, x, random.choice(good_colors))
        self.gameState_string += "moved! "
        self.print_board()

    def make_move(self, move: str) -> int:
        score = 0
        self.gameState_string = ""

        if self.is_exploding:
            set1 = map(tuple, self.remove_cells)
            score = len(set(set1))
            self.explode()

            self.gameState_string += "exploded! "
            self.print_board()
        elif self.is_falling:
            self.fall()
            self.gameState_string += "fell! "
            self.print_board()
            self.remove_cells = self.get_triplets()
            if len(self.remove_cells):
                #self.gameState_string += "found triplet! "
                self.is_exploding = True
        elif move != "":
            x1, y1, x2, y2 = [int(i) for i in move.split()]  # TODO: swap y & x
            self.board[x1][y1], self.board[x2][y2] = (
                self.board[x2][y2],
                self.board[x1][y1],
            )
            self.gameState_string += "moved! "
            self.print_board()
            self.remove_cells = self.get_triplets()
            if len(self.remove_cells):
                #self.gameState_string += "found triplet! "
                self.is_exploding = True
        else:
            raise Exception(
                "Edmund McMillen. You little fucker. You made a shit of piece with your trash Isaac. "
                "It’s fucking bad this trash game. I will become back my money. "
                "I hope you will in your next time a cow; on a trash farm, you sucker. "
            )

        self.GameState.append(self.gameState_string)
        return score

    def explode(self):
        for cell in self.remove_cells:
            self.board[cell[0]][cell[1]] = Gem(cell[0], cell[1], "Empty")
        self.is_exploding = False
        self.is_falling = True

    def fall(self):
        # -2 because the last row never falls
        for y in range(COLS_NUM - 2, -1, -1):
            for x in range(ROWS_NUM - 1, -1, -1):
                x_offset = 1  # actually y_offset, see TODO
                while y + x_offset <= COLS_NUM - 1:
                    if self.board[y + x_offset][x].color != "Empty":
                        break
                    x_offset += 1
                x_offset -= 1  # TODO: I hate my life
                if x_offset != 0:
                    self.board[y + x_offset][x].color = self.board[y][x].color
                    self.board[y][x].color = "Empty"

        # now generate random
        for y in range(COLS_NUM):
            for x in range(ROWS_NUM):
                if self.board[y][x].color == "Empty":
                    self.board[y][x].color = random.choice(COLORS)
        self.is_falling = False

    def get_triplets(self) -> list[list[int]]:
        elements_to_delete = []

        # Здесь y и x наоборот, вроде похуй
        for y in range(COLS_NUM):
            for x in range(ROWS_NUM):
                y_add, x_add = 1, 1
                x_elements= []
                y_elements = []
                # check vertical
                while y + y_add < COLS_NUM:
                    if self.board[y][x].color != self.board[y + y_add][x].color:
                        break
                    if [y + y_add, x] not in x_elements:
                        x_elements.append([y + y_add, x])
                    y_add += 1
                # check horizontal
                while x + x_add < ROWS_NUM:
                    if self.board[y][x].color != self.board[y][x + x_add].color:
                        break
                    if [y, x + x_add] not in y_elements:
                        y_elements.append([y, x + x_add])
                    x_add += 1

                if y_add >= 3 or x_add >= 3:
                    elements_to_delete.append([y, x])

                if y_add >= 3 and x_add >= 3:
                    elements_to_delete.extend(x_elements)
                    elements_to_delete.extend(y_elements)
                elif y_add >= 3:
                    elements_to_delete.extend(x_elements)
                elif x_add >= 3:
                    elements_to_delete.extend(y_elements)

        return elements_to_delete

    def get_moves(self) -> list[str]:
        if self.is_exploding or self.is_falling:
            return ['']

        moves = []

        for y in range(COLS_NUM):
            for x in range(ROWS_NUM):
                if y + 1 < COLS_NUM:
                    moves.append(f"{y} {x} {y+1} {x}")
                if x + 1 < ROWS_NUM:
                    moves.append(f"{y} {x} {y} {x+1}")
        if not moves:
            return ['']
        return moves

    def show_game(self, start: int, end: int) -> list[str]:
        return self.GameState[start:end]

    # X, O, T
    def print_board(self):
        color_to_ascii = {"r": "X", "g": "O", "b": "T", "E": "_", "R": "R"}
        for i in range(ROWS_NUM):
            mystring = [
                color_to_ascii[self.board[i][j].color[0]] for j in range(COLS_NUM)
            ]
            self.gameState_string += "".join(mystring) + " "

        #print(self.gameState_string)
        # print()


class Gem:
    def __init__(self, y, x, color):
        self.color = color
        self.y = y
        self.x = x


if __name__ == '__main__':
    g = ThreeInRow()
    g.print_board()
    # inp = input() # TODO: везде все наоборот, а не похуй ли?
    for i in range(25):
        moves = g.get_moves()
        if len(moves):
            score = g.make_move(random.choice(moves))
        else:
            score = g.make_move("")
        print(score)
        time.sleep(1)
    with open(r'output.txt', 'w') as fp:
        for item in g.GameState:
            fp.write("%s\n" % item)
        print('Done')
    print(g.GameState)
