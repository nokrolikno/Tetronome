import pygame as pg
import pygame.draw

import pymunk.pygame_util
from pymunk import Circle, Body, moment_for_circle
from random import randrange

from source import DynamicGame

pymunk.pygame_util.positive_y_is_up = False

VAL_COL_DICT = {
    '0.1': (136, 69, 53, 0),
    '0.25': (250, 210, 1, 0),
    '0.5': (245, 119, 10, 0),
    '2': (77, 93, 83, 0),
    '2.5': (77, 93, 83, 0),
    '5': (77, 93, 83, 0),
    '20': (77, 93, 83, 0),
    '100': (77, 93, 83, 0),
    '1000': (77, 93, 83, 0),
}


class Gaussian_Lud:

    def __init__(self, space, W, H):

        self.space = space
        self.height = H
        self.width = W

        # For pyramid
        self.center = self.width // 2
        self.n_pin_rows = 16
        self.pin_radius = 8
        self.offset_x = self.offset_y = self.pin_radius * 2 * 3

        # For boxes
        self.n_boxes = self.n_pin_rows + 1
        self.box_side = 0.9 * self.offset_x

        # For luda-ball
        self.ball_mass = 1
        self.ball_radius = self.pin_radius * 1.5

        self.board = []
        self.borders = []
        self.x_boxes = []

        self.border_elasticity = .8
        self.border_friction = 1

    def pyramid_coords_generator(self):

        running_y = int(self.height * 0.15)
        row_start = self.center - self.offset_x
        for row in range(self.n_pin_rows):
            n_pins = row + 3
            running_x = row_start
            while n_pins > 0:

                yield running_x, running_y
                running_x += self.offset_x
                n_pins -= 1

            row_start -= self.offset_x / 2
            running_y += self.offset_y

    def xboxes_coords_generator(self, x, y):

        running_x = x + self.offset_x // 2
        y += self.box_side

        for _ in range(self.n_boxes):
            yield running_x, y
            running_x += self.offset_x

    def fill_board(self):

        # Pins
        row = []
        for x, y in self.pyramid_coords_generator():
            pin = Pin(x, y, self.pin_radius)
            pin.insert_pin(self.space)
            if len(row) > 1 and pin.y != row[-1].y:
                self.board.append(row)
                row = [pin]
                continue
            row.append(pin)
        self.board.append(row)

        # Borders
        left_border = pymunk.Segment(body=self.space.static_body,
                                     a=(self.board[0][0].x - self.offset_x // 2, self.board[0][0].y),
                                     b=(self.board[-1][0].x - self.offset_x // 2, self.board[-1][0].y),
                                     radius=self.pin_radius // 2)

        right_border = pymunk.Segment(body=self.space.static_body,
                                      a=(self.board[0][-1].x + self.offset_x // 2, self.board[0][0].y),
                                      b=(self.board[-1][-1].x + self.offset_x // 2, self.board[-1][0].y),
                                      radius=self.pin_radius // 2)

        self.borders.extend([left_border, right_border])

        self.space.add(left_border)
        self.space.add(right_border)
        left_border.elasticity = self.border_elasticity
        right_border.friction = self.border_friction

        # X-boxes
        for x, y in self.xboxes_coords_generator(self.board[-1][0].x, self.board[-1][0].y):
            box = XBox(x, y, self.box_side, 0.5)
            self.x_boxes.append(box)
            box.insert_box(self.space)



    def generate_ludoball(self):
        ball_moment = moment_for_circle(self.ball_mass, 0, self.ball_radius)
        ball_body = Body(self.ball_mass, ball_moment)
        ball_body.position = (randrange(start=self.center - self.offset_x + 1, stop=self.center + self.offset_x), 0)
        ball_shape = Circle(ball_body, self.ball_radius)
        ball_shape.elasticity = 0.8
        ball_shape.friction = 1.0
        ball_shape.color = [randrange(256) for i in range(4)]
        self.space.add(ball_body, ball_shape)


class Pin:
    """
        A class to represent a pintle on a game board.

        ...

        Attributes
        ----------
        x, y : float, float
            coords of the center of a pintle
        radius : float
            idk, something useful maybe...
        elasticity : float
            eeemmm... color?
        friction : float
            WHAT DA HAIL?!

        Methods
        -------
        insert_pintle(space):
            Generates a single pintle on a game board
    """

    def __init__(self, x, y, radius=5):
        # Core body properties
        self.x = x
        self.y = y
        self.radius = radius
        self.elasticity = .3
        self.friction = 1.0
        self.color = (77, 93, 83, 0)

        # Initializing essential Body and Shape abstractions
        self.body = Body(body_type=Body.STATIC)
        self.body.position = self.x, self.y

        self.shape = Circle(self.body, self.radius)
        self.shape.elasticity = self.elasticity
        self.shape.friction = self.friction
        self.shape.color = self.color

    def insert_pin(self, space):
        space.add(self.body, self.shape)


class XBox:

    def __init__(self, x, y, side, value):
        self.x = x
        self.y = y
        self.side = side
        self.value = value
        self.elasticity = .3
        self.friction = 1.0

        self.color = VAL_COL_DICT[str(self.value)]

        # Initializing essential Body and Shape abstractions
        self.body = Body(body_type=Body.STATIC)
        self.body.position = (self.x, self.y)

        self.shape = pymunk.Poly.create_box(self.body, (self.side, self.side))
        self.shape.color = self.color
        self.shape.elasticity = self.elasticity
        self.shape.friction = self.friction

    def insert_box(self, space):
        space.add(self.body, self.shape)





# segment_shape = pymunk.Segment(space.static_body, (2, HEIGHT), (WIDTH, HEIGHT), 26)
# space.add(segment_shape)
# segment_shape.elasticity = 0.8
# segment_shape.friction = 1.0


def init_playground(W, H):

    pg.init()
    surface = pg.display.set_mode((W, H))
    clock = pg.time.Clock()
    space = pymunk.Space()
    space.gravity = 0, 4e3

    return surface, space, clock

def create_square(space, pos):
    square_mass, square_size = 1, (60, 60)
    square_moment = pymunk.moment_for_box(square_mass, square_size)
    square_body = pymunk.Body(square_mass, square_moment)
    square_body.position = pos
    square_shape = pymunk.Poly.create_box(square_body, square_size)
    square_shape.elasticity = 0.8
    square_shape.friction = 1.0
    square_shape.color = [randrange(256) for i in range(4)]
    space.add(square_body, square_shape)


# segment_shape = pymunk.Segment(space.static_body, (2, HEIGHT), (WIDTH, HEIGHT), 26)
# space.add(segment_shape)
# segment_shape.elasticity = 0.8
# segment_shape.friction = 1.0

def main():

    WIDTH, HEIGHT = 900, 1200
    FPS = 60

    surface, space, clock = init_playground(W=WIDTH, H=HEIGHT,)

    draw_options = pymunk.pygame_util.DrawOptions(surface)

    game = Gaussian_Lud(space=space, W=WIDTH, H=HEIGHT)
    game.fill_board()

    while True:
        surface.fill(pg.Color('grey'))

        for i in pg.event.get():
            if i.type == pg.QUIT:
                exit()

            if i.type == pg.MOUSEBUTTONDOWN:
                if i.button == 1:
                    game.generate_ludoball()
                    #create_square(space, i.pos)
                    # pintle = Pintle(randrange(500), randrange(500), radius=30)
                    # pintle.insert_pintle(space=space)
                    #print(i.pos)

        space.debug_draw(draw_options)
        space.step(1 / FPS)

        pg.display.flip()
        clock.tick(FPS)

    print('end')

if __name__ == "__main__":
    main()