import pygame as p
import random
import time
import os
import re
import math

ascii_to_sprite = {"X": "cherry", "O": "chockolate", "T": "cupcake", "Y": 'donut', 'M': 'lollipop'}

FPS = 46
BASE_IMG_DIR = 'images/'
WORKING_DIR = './'


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
        self.action_ticks = 20

    def moving_function(self, x):
        return -1.5 * x**2 + 2.5 * x

    def set_action_ticks(self, ticks: int):
        self.action_ticks = ticks

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
            if self.moving_state >= self.action_ticks:
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
                (end_center_x - start_center_x) * self.moving_function(self.moving_state / self.action_ticks)
            )
            new_center_y = start_center_y + int(
                (end_center_y - start_center_y) * self.moving_function(self.moving_state / self.action_ticks)
            )
            self.rect = self.image.get_rect(center=(new_center_x, new_center_y))
        elif self.action == 'dying':
            self.dying_state += 1
            if self.dying_state >= self.action_ticks:
                self.kill()
            transparency = 180
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
    COMBO_COLORS = [(39, 253, 245), (247, 101, 184)]
    TIN_COLOR = COMBO_COLORS[0]
    PINK_COLOR = COMBO_COLORS[1]

    def __init__(self, board_size_x, board_size_y, x_margin, y_margin, init_board, tmp_vid_folder='tmp_vid/'):
        p.init()
        self.board_size_x = board_size_x
        self.board_size_y = board_size_y
        self.x_margin = x_margin
        self.y_margin = y_margin
        self.cell_size = (self.WIDTH - 2 * self.x_margin) // self.board_size_x
        self.center = self.WIDTH // 2, self.y_margin + (self.cell_size * self.board_size_y) // 2

        self.screen = p.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = p.time.Clock()
        self.screen.fill(self.BACKGROUND_COLOR)
        self.gems = p.sprite.Group()
        self.board = []

        # Score & Combo stuff
        self.score = random.randint(10, 1000)
        self.current_frame = 0
        self.combo = 'x1'
        self.color_diff = [self.TIN_COLOR[i] - self.PINK_COLOR[i] for i in range(3)]
        self.cur_color = self.TIN_COLOR
        self.cur_angle = 0
        self.combo_color_cnt = 0
        self.combo_angle_add = 1

        self.score_font = p.font.Font(WORKING_DIR + 'AlfaSlabOne-Regular.ttf', y_margin // 2)
        self.combo_font = p.font.Font(WORKING_DIR + 'AlfaSlabOne-Regular.ttf', y_margin // 2)

        # Add rotation around point for Combo (no kak?)
        self.x_around_circle = 0
        self.x_around_add = 1
        self.y_around_circle = 10
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
        # self.screen.fill(self.BACKGROUND_COLOR, (0, 0, self.WIDTH, self.y_margin))
        self.screen.blit(scoreSurfaceObj, scoreRectObj)

        myimage = p.image.load(BASE_IMG_DIR + "chelibobes.png")
        imagerect = myimage.get_rect()
        imagerect.topleft = (-75, self.HEIGHT * 2 // 3)
        self.screen.blit(myimage, imagerect)

    def draw_combo(self):
        self.combo_font = p.font.Font(
            WORKING_DIR + 'AlfaSlabOne-Regular.ttf', min(self.y_margin // 10 + int(self.combo[1:]) * 2, 72)
        )
        self.cur_color = [self.cur_color[i] - int(self.color_diff[i] / 10) for i in range(3)]
        if int(self.combo_color_cnt) == 9:
            self.color_diff = [-self.color_diff[i] for i in range(3)]
            self.combo_color_cnt = 0

        if abs(self.cur_angle) == 15:
            self.combo_angle_add *= -1

        if round(abs(self.x_around_circle)) == 10:
            self.x_around_add *= -1

        comboSurfaceObj = self.combo_font.render(f'COMBO!!: {self.combo}', True, self.cur_color)
        comboAddSurfaceObj = self.combo_font.render(f'COMBO!!: {self.combo}', True, 'black')
        comboSurfaceObj = p.transform.rotate(comboSurfaceObj, self.cur_angle)
        comboAddSurfaceObj = p.transform.rotate(comboAddSurfaceObj, self.cur_angle)
        comboRectObj = comboSurfaceObj.get_rect()
        comboAddRectObj = comboAddSurfaceObj.get_rect()
        comboRectObj.center = (
            self.WIDTH // 2 + self.x_around_circle,
            self.y_margin + (self.cell_size * self.board_size_y) // 2 + self.y_around_circle,
        )
        comboAddRectObj.center = (
            self.WIDTH // 2 + self.x_around_circle // 1.5,
            self.y_margin + (self.cell_size * self.board_size_y) // 2 + self.y_around_circle // 1.5,
        )

        self.screen.blit(comboSurfaceObj, comboRectObj)
        self.screen.blit(comboAddSurfaceObj, comboAddRectObj)
        self.combo_color_cnt += 1
        self.cur_angle += self.combo_angle_add
        self.x_around_circle += self.x_around_add
        y_pos = math.sqrt(100 - min(self.x_around_circle**2, 100))

        self.y_around_circle = y_pos if self.x_around_add == 1 else -y_pos

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
        self.combo = combo
        if move_description == 'moved!':
            self.move_gems(self.previous_board, board)
        elif move_description == 'exploded!':
            self.explode_gems(self.previous_board, board)
        elif move_description == 'fell!':
            self.fall_gems(self.previous_board, board)
        self.update_until_beat()
        self.previous_board = board

    def update_until_beat(self):
        for i in range(FPS):
            self.screen.fill(self.BACKGROUND_COLOR)
            self.gems.update()
            self.draw_score()
            self.draw_grid()
            self.gems.draw(self.screen)
            self.clock.tick(FPS)

            self.draw_combo()

            p.display.flip()
            p.image.save(self.screen, WORKING_DIR + 'tmp_vid/{:05d}.png'.format(self.current_frame))
            self.current_frame += 1


def make_frames(source_dir, game_filename, tmp_vid_folder, fps, working_dir='./'):
    folder_path = tmp_vid_folder
    global FPS
    global BASE_IMG_DIR
    global WORKING_DIR
    FPS = fps
    BASE_IMG_DIR = source_dir
    WORKING_DIR = working_dir

    all_tmp_vid = os.listdir(folder_path)

    for images in all_tmp_vid:
        if images.endswith(".png"):
            os.remove(os.path.join(folder_path, images))
    with open(game_filename, 'r') as file:
        lines = file.readlines()
    parts = lines[0].strip().split()
    board = parts[3:]
    engine = Engine(len(board[0]), len(board), 20, 100, board, tmp_vid_folder=tmp_vid_folder)
    for line in lines[1:]:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        parts = line.strip().split()
        move_description, score, combo, *board = parts
        engine.make_move(move_description, score, combo, board)
        engine.clock.tick(FPS)
        p.display.flip()


def main():
    folder_path = './tmp_vid/'

    all_tmp_vid = os.listdir(folder_path)

    for images in all_tmp_vid:
        if images.endswith(".png"):
            os.remove(os.path.join(folder_path, images))
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
