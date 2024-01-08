import pygame as p
import random
import time

cell_size = 60
ascii_to_color = {'X': 'red', 'O': 'green', 'T': 'blue', '_': 'black'}
board_with_underscores = []


def drawBoard(board, screen):
    for i in range(len(board)):
        for j in range(len(board[i])):
            p.draw.rect(
                screen,
                ascii_to_color[board[j][i]],
                (60 * j, 60 * i, 60 - 2, 60 - 2),
                border_radius=8,
            )


def explodeBoard(board, screen):
    for i in range(len(board)):
        for j in range(len(board[i])):
            p.draw.rect(
                screen,
                ascii_to_color[board[j][i]],
                (60 * j, 60 * i, 60 - 2, 60 - 2),
                border_radius=8,
            )


def fallBoard(board, board_with_underscores, screen):
    # print(board_with_underscores)
    holes_cnt = [0 for _ in range(10)]
    holes_fillings = [[] for _ in range(10)]
    fall_list = []
    additional_draw = []
    for y in range(10 - 2, -1, -1):
        for x in range(10 - 1, -1, -1):
            if board_with_underscores[y][x] == '_':
                holes_cnt[y] += 1
    for y in range(10):
        holes_fillings[y] = [board[y][i] for i in range(holes_cnt[y] - 1, -1, -1)]
        # from, to, color
        fall_list.extend([[[y, i - holes_cnt[y]], [y, i], board[y][i]] for i in range(holes_cnt[y] - 1, -1, -1)])
    print(fall_list)

    for y in range(10 - 2, -1, -1):
        for x in range(10 - 1, -1, -1):
            need_to_fall = 0
            x_offset = 1  # actually y_offset, see TODO
            while x + x_offset <= 10 - 1:
                if board_with_underscores[y][x + x_offset] == '_':
                    need_to_fall += 1
                x_offset += 1
            x_offset -= 1  # TODO: I hate my life
            if need_to_fall != 0:
                fall_list.append([[y, x], [y, x + need_to_fall], board_with_underscores[y][x]])
                print('БЛЯЯЯЯЯть', need_to_fall)
                # board_with_underscores[y + x_offset][x].color = self.board[y][x].color
                # board_with_underscores[y][x].color = 'Empty'

    # fall
    while len(fall_list):
        screen.fill(p.Color('black'))
        # draw static
        for i in range(len(board_with_underscores)):
            for j in range(len(board_with_underscores[i])):
                if [i, j] not in [fall_list[k][0] for k in range(len(fall_list))]:
                    # pass
                    # print('I draw static!')
                    p.draw.rect(
                        screen,
                        ascii_to_color[board_with_underscores[i][j]],
                        (60 * i, 60 * j, 60 - 2, 60 - 2),
                        border_radius=8,
                    )

        for el in additional_draw:
            pass
            # p.draw.rect(screen, ascii_to_color[el[1]],
            #            (60 * el[0][0], 60 * el[0][1], 60 - 2, 60 - 2), border_radius=8)

        # print('start drawing animation!')
        for i in range(len(fall_list) - 1, -1, -1):
            p.draw.rect(
                screen,
                ascii_to_color[fall_list[i][2]],
                (60 * fall_list[i][0][0], 60 * fall_list[i][0][1], 60 - 2, 60 - 2),
                border_radius=8,
            )

            if fall_list[i][0] == fall_list[i][1]:
                additional_draw.append([fall_list[i][0], fall_list[i][2]])
                # board_with_underscores[fall_list[i][0][0]][fall_list[i][0][1]] = fall_list[i][2]
                del fall_list[i]
                continue

            fall_list[i][0][0], fall_list[i][0][1] = (
                fall_list[i][0][0],
                fall_list[i][0][1] + 0.5,
            )
            p.display.flip()
        time.sleep(1)
        print('finished all!', len(fall_list))


def parseMove(move, screen):
    # p.draw.rect(screen, 'red', (-100, -100, 60 - 2, 60 - 2), border_radius=8)
    global board_with_underscores
    parts = move.split()
    move_description, board = parts[0], parts[1:]
    if move_description == 'moved!':  # first position or move done
        drawBoard(board, screen)
    elif move_description == 'exploded!':
        explodeBoard(board, screen)
        board_with_underscores = board.copy()
    elif move_description == 'fell!':
        fallBoard(board, board_with_underscores, screen)
    else:
        raise Exception('Чё то странное в ходах попалось')


def playGame(moves):
    p.init()
    screen = p.display.set_mode((600, 600))
    clock = p.time.Clock()
    screen.fill(p.Color('black'))

    running = True
    move_index = 0
    while running:
        if move_index < len(moves):
            parseMove(moves[move_index], screen)
        else:
            running = False

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

        move_index += 1
        clock.tick(1)
        time.sleep(1)
        p.display.flip()


if __name__ == '__main__':
    file1 = open('output.txt', 'r')
    Lines = file1.readlines()
    playGame(Lines)
