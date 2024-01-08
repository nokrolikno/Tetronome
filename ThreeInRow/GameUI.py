import pygame as p
import random
import time
import os
import re


ascii_to_color = {'X': 'red', 'O': 'green', 'T': 'blue', '_': 'black'}
ascii_to_sprite = {'X': 'cherry', 'O': 'chockolate', 'T': 'cupcake'}

FPS = 30
BASE_IMG_DIR = 'images/'


class Gem(p.sprite.Sprite):
    SMALLNESS = 17

    def __init__(self, x, y, cell_size, filename):
        p.sprite.Sprite.__init__(self)
        self.cell_size = cell_size
        regex = re.compile(filename + r'[0-9]+\.png')
        self.max_file = 1
        for root, dirs, files in os.walk(BASE_IMG_DIR):
            for file in files:
                if regex.match(file) and int(file[-6:-4]) > self.max_file:
                    self.max_file = int(file[-6:-4])
        self.state = 1
        self.filename = filename
        self.image = p.image.load(BASE_IMG_DIR + filename + '{:02d}'.format(self.state) + '.png').convert_alpha()
        self.image = p.transform.scale(self.image, (cell_size - self.SMALLNESS, cell_size - self.SMALLNESS))
        self.rect = self.image.get_rect(center=(x + cell_size // 2, y + cell_size // 2))
        self.action = 'stationary'
        self.a_x, self.a_y, self.b_x, self.b_y = 0, 0, 0, 0
        self.moving_state = 0
        self.dying_state = 0

    def moving_function(self, x):
        return -1.5 * x**2 + 2.5 * x

    def update(self):
        if self.action == 'stationary':
            if random.random() < 0.1:
                self.state = (self.state + 1) % self.max_file + 1
                self.image = p.image.load(
                    BASE_IMG_DIR + self.filename + '{:02d}'.format(self.state) + '.png'
                ).convert_alpha()
                self.image = p.transform.scale(
                    self.image,
                    (self.cell_size - self.SMALLNESS, self.cell_size - self.SMALLNESS),
                )
        elif self.action == 'moving':
            self.moving_state += 1
            if self.moving_state >= 10:
                self.action = 'stationary'
            start_center_x, start_center_y = (
                self.a_x + self.cell_size // 2,
                self.a_y + self.cell_size // 2,
            )
            end_center_x, end_center_y = (
                self.b_x + self.cell_size // 2,
                self.b_y + self.cell_size // 2,
            )
            new_center_x = start_center_x + int(
                (end_center_x - start_center_x) * self.moving_function(self.moving_state / 10)
            )
            new_center_y = start_center_y + int(
                (end_center_y - start_center_y) * self.moving_function(self.moving_state / 10)
            )
            self.rect = self.image.get_rect(center=(new_center_x, new_center_y))
        elif self.action == 'dying':
            self.dying_state += 1
            if self.dying_state >= 10:
                self.kill()
            transparency = 128
            self.image.fill((255, 255, 255, transparency), special_flags=p.BLEND_RGBA_MULT)

    def move(self, a_x, a_y, b_x, b_y):
        self.a_x, self.a_y, self.b_x, self.b_y = a_x, a_y, b_x, b_y
        self.action = 'moving'
        self.moving_state = 0

    def die(self):
        self.action = 'dying'
        self.dying_state = 0


class Engine:
    WIDTH, HEIGHT = 560, 900
    GRID_COLOR = (128, 128, 128)
    CELL_COLOR_A = (179, 179, 179)
    CELL_COLOR_B = (153, 153, 153)
    BACKGROUND_COLOR = (255, 192, 203)
    GRID_THICKNESS = 5

    def __init__(self, board_size_x, board_size_y, x_margin, y_margin, init_board):
        p.init()
        self.board_size_x = board_size_x
        self.board_size_y = board_size_y
        self.x_margin = x_margin
        self.y_margin = y_margin
        self.cell_size = (self.WIDTH - 2 * self.x_margin) // self.board_size_x
        self.screen = p.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = p.time.Clock()
        self.screen.fill(self.BACKGROUND_COLOR)
        self.gems = p.sprite.Group()
        self.board = []
        self.score = random.randint(10, 1000)

        self.score_font = fontObj = p.font.Font('AlfaSlabOne-Regular.ttf', y_margin // 2)

        myimage = p.image.load("images/chelibobes.png")
        imagerect = myimage.get_rect()
        imagerect.topleft = (-75, self.HEIGHT * 2 // 3)
        self.screen.blit(myimage, imagerect)

        for i in range(board_size_x):
            col = []
            for j in range(board_size_y):
                if init_board[j][i] == '_':
                    col.append(None)
                    continue
                gem = Gem(
                    self.x_margin + i * self.cell_size,
                    self.y_margin + j * self.cell_size,
                    self.cell_size,
                    ascii_to_sprite[init_board[j][i]],
                )
                col.append(gem)
                self.gems.add(gem)
            self.board.append(col)
        self.previous_board = init_board
        self.draw_grid()

    def draw_score(self):
        scoreSurfaceObj = self.score_font.render(f'Score: {self.score}', True, (0, 0, 0))
        scoreRectObj = scoreSurfaceObj.get_rect()
        scoreRectObj.topleft = (self.WIDTH // 4, self.y_margin // 4)
        self.screen.fill(self.BACKGROUND_COLOR, (0, 0, self.WIDTH, self.y_margin))
        self.screen.blit(scoreSurfaceObj, scoreRectObj)

    def draw_grid(self):
        for i in range(self.board_size_x):
            for j in range(self.board_size_y):
                color = self.CELL_COLOR_A if (i + j) % 2 else self.CELL_COLOR_B
                p.draw.rect(
                    self.screen,
                    color,
                    (
                        self.x_margin + i * self.cell_size,
                        self.y_margin + j * self.cell_size,
                        self.cell_size,
                        self.cell_size,
                    ),
                )
        for i in range(
            self.x_margin,
            self.WIDTH - self.x_margin + 1,
            self.cell_size,
        ):
            p.draw.rect(
                self.screen,
                self.GRID_COLOR,
                (
                    i,
                    self.y_margin,
                    self.GRID_THICKNESS,
                    self.board_size_y * (self.WIDTH - 2 * self.x_margin) // self.board_size_x + self.GRID_THICKNESS,
                ),
            )
        for i in range(
            self.y_margin,
            self.y_margin + self.cell_size * self.board_size_y + 1,
            self.cell_size,
        ):
            p.draw.rect(
                self.screen,
                self.GRID_COLOR,
                (self.x_margin, i, self.WIDTH - 2 * self.x_margin, self.GRID_THICKNESS),
            )

    def move_gems(self, previous_board, board):
        gem_a_i, gem_a_j, gem_b_i, gem_b_j = -1, -1, -1, -1
        for i in range(self.board_size_x):
            for j in range(self.board_size_y):
                if previous_board[j][i] == board[j][i]:
                    continue
                if gem_a_i < 0:
                    gem_a_i, gem_a_j = i, j
                    continue
                gem_b_i, gem_b_j = i, j
        self.board[gem_a_i][gem_a_j].move(
            self.x_margin + self.cell_size * gem_a_i,
            self.y_margin + self.cell_size * gem_a_j,
            self.x_margin + self.cell_size * gem_b_i,
            self.y_margin + self.cell_size * gem_b_j,
        )
        self.board[gem_b_i][gem_b_j].move(
            self.x_margin + self.cell_size * gem_b_i,
            self.y_margin + self.cell_size * gem_b_j,
            self.x_margin + self.cell_size * gem_a_i,
            self.y_margin + self.cell_size * gem_a_j,
        )
        self.board[gem_a_i][gem_a_j], self.board[gem_b_i][gem_b_j] = (
            self.board[gem_b_i][gem_b_j],
            self.board[gem_a_i][gem_a_j],
        )

    def explode_gems(self, previous_board, board):
        exploded = []
        for i in range(self.board_size_x):
            for j in range(self.board_size_y):
                if previous_board[j][i] != board[j][i]:
                    exploded.append((i, j))
        for i, j in exploded:
            self.board[i][j].die()

    def fall_gems(self, previous_board, board):
        empty_under = [[0 for j in range(self.board_size_y)] for i in range(self.board_size_x)]
        for i in range(self.board_size_x):
            for j in range(self.board_size_y - 1, -1, -1):
                if j == self.board_size_y - 1:
                    if previous_board[j][i] == '_':
                        empty_under[i][j] = 1
                    continue
                empty_under[i][j] = empty_under[i][j + 1] + 1 if previous_board[j][i] == '_' else empty_under[i][j + 1]
        for i in range(self.board_size_x):
            for j in range(self.board_size_y - 1, -1, -1):
                if empty_under[i][j] != 0 and previous_board[j][i] != '_':
                    self.board[i][j].move(
                        self.x_margin + self.cell_size * i,
                        self.y_margin + self.cell_size * j,
                        self.x_margin + self.cell_size * i,
                        self.y_margin + self.cell_size * (j + empty_under[i][j]),
                    )
                    self.board[i][j + empty_under[i][j]] = self.board[i][j]
                if j - empty_under[i][0] < 0:
                    self.board[i][j] = Gem(
                        self.x_margin + self.cell_size * i,
                        self.y_margin + self.cell_size * 0,
                        self.cell_size,
                        ascii_to_sprite[board[j][i]],
                    )
                    self.gems.add(self.board[i][j])
                    self.board[i][j].move(
                        self.x_margin + self.cell_size * i,
                        self.y_margin + self.cell_size * 0,
                        self.x_margin + self.cell_size * i,
                        self.y_margin + self.cell_size * j,
                    )

    def make_move(self, move_description, score, combo, board):
        self.score += int(score)
        if move_description == 'moved!':
            self.move_gems(self.previous_board, board)
        elif move_description == 'exploded!':
            self.explode_gems(self.previous_board, board)
        elif move_description == 'fell!':
            self.fall_gems(self.previous_board, board)
        self.update_until_beat()
        self.previous_board = board

    def update_until_beat(self):
        for i in range(20):
            self.gems.update()
            self.draw_score()
            self.draw_grid()
            self.gems.draw(self.screen)
            self.clock.tick(FPS)
            p.display.flip()


def main():
    with open('output.txt', 'r') as file:
        lines = file.readlines()
    parts = lines[0].strip().split()
    board = parts[3:]
    engine = Engine(len(board[0]), len(board), 20, 100, board)
    for line in lines[1:]:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        parts = line.strip().split()
        move_description, score, combo, *board = parts
        engine.make_move(move_description, score, combo, board)
        engine.clock.tick(FPS)
        p.display.flip()


if __name__ == '__main__':
    main()
