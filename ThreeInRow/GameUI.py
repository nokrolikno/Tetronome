import pygame as p
import random
import time
import os


cell_size = 100
ascii_to_color = {"X": "red", "O": "green", "T": "blue", '_': 'black'}
ascii_to_sprite = {'X': 'cherry', 'O': 'chockolate', 'T': 'cupcake'}


class Gem(p.sprite.Sprite):
    def __init__(self, x, y, filename):
        p.sprite.Sprite.__init__(self)
        self.image = p.image.load(filename).convert_alpha()
        self.image = p.transform.scale(self.image, (cell_size, cell_size))
        self.rect = self.image.get_rect(center=(x + cell_size // 2, y + cell_size // 2))

class GameState:
    def __init__(self):
        p.init()
        self.screen = p.display.set_mode((cell_size * 10, cell_size * 10))
        self.clock = p.time.Clock()
        self.screen.fill(p.Color("black"))

        file1 = open('output.txt', 'r')
        self.moves = file1.readlines()
        self.move_cnt = 0

        self.gems = p.sprite.Group()

        self.previous_board = []



    def makeMove(self):
        self.screen.fill(p.Color("black"))
        #print(self.move_cnt)
        parts = self.moves[self.move_cnt].split()
        move_description, board = parts[0], parts[1:]
        if move_description == 'moved!':
            self.drawBoard(board)
        elif move_description == 'exploded!':
            #self.gems.draw(self.screen)
            raise NotImplementedError
            #explodeBoard(board, screen)
        elif move_description == 'fell!':
            raise NotImplementedError
            #fallBoard(board, board_with_underscores, screen)
        self.previous_board = board
        self.move_cnt += 1


    def drawBoard(self, board):
        for i in range(len(board)):
            for j in range(len(board[i])):
                self.gems = p.sprite.Group()
                first_image = [f for f in os.listdir('images') if f.find('01') != -1 and f.find(ascii_to_sprite[board[j][i]]) != -1][0]
                other_images = [f for f in os.listdir('images') if f.find('01') == -1 and f.find(ascii_to_sprite[board[j][i]]) != -1]
                if len(self.previous_board):
                    if board[j][i] == self.previous_board[j][i]:
                        self.gems.add(Gem(i * cell_size, j * cell_size, f"images/{random.choice(other_images)}"))
                    else:
                        self.gems.add(Gem(i*cell_size, j*cell_size, f'images/{first_image}'))
                else:
                    self.gems.add(Gem(i*cell_size, j*cell_size, f'images/{first_image}'))


                self.gems.draw(self.screen)
                #p.draw.rect(self.screen, ascii_to_color[board[i][j]], (60 * j, 60 * i, 60 - 2, 60 - 2), border_radius=8)


def main():
    engine = GameState()

    running = True
    #move_index = 0
    while running:
        if engine.move_cnt < len(engine.moves):
            engine.makeMove()
        else:
            running = False

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

        engine.clock.tick(1)
        #time.sleep(3)

        p.display.flip()


if __name__ == '__main__':
    main()





