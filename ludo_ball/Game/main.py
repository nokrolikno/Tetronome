import pygame as pg
import pygame.draw

import pymunk.pygame_util
from pymunk import Circle, Body, moment_for_circle, Poly
from random import randrange

from source import DynamicGame

pymunk.pygame_util.positive_y_is_up = False


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
        self.n_boxes = 17
        self.

        # For luda-ball
        self.ball_mass = 1
        self.ball_radius = self.pin_radius * 1.5

        self.board = []

    def coords_generator(self):

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

    def fill_board(self):

        for x, y in self.coords_generator():
            pin = Pin(x, y, self.pin_radius)
            self.board.append(Pin(x, y, self.pin_radius))
            pin.insert_pin(self.space)




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
        # pygame.draw.circle(surface=display,
        #                    color=self.color,
        #                    center=self.body.position,
        #                    radius=self.radius)


class X_box:

    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value




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