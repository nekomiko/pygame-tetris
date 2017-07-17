from grid import Grid
from game import Score
import random
import time
import pygame
from pygame.locals import *
FIGURES_unproc = [
    [
        ["X", "X"],
        ["X", "X"]
    ],
    [
        [" ", "X", " "],
        ["X", "X", "X"],
        [" ", " ", " "]],
    [
        ["X", " ", " "],
        ["X", "X", " "],
        [" ", "X", " "]
    ],
    [
        [" ", " ", "X", " "],
        [" ", " ", "X", " "],
        [" ", " ", "X", " "],
        [" ", " ", "X", " "]
    ],
    [
        ["X", " ", " "],
        ["X", "X", "X"],
        [" ", " ", " "]
    ]
]


def rotate_figure(figure):
    n = len(figure)
    m = len(figure[0])
    r_figure = [[" " for i in range(n)] for j in range(m)]
    for i in range(n):
        for j in range(m):
            r_figure[j][i] = figure[i][m - 1 - j]
    return r_figure


def preprocess_figures(figures_unproc):
    figures = [[] for i in range(len(figures_unproc))]
    for i in range(len(figures_unproc)):
        f_rot = figures[i]
        figure = figures_unproc[i]
        for j in range(0, 4):
            f_rot.append(figure)
            figure = rotate_figure(figure)
    return figures


FIGURES = preprocess_figures(FIGURES_unproc)

class TetrisGameOver(Exception):
    pass

class TetrisModel:
    cell_color = "#FF00FF"
    move_delay = 0.250

    def __init__(self, grid):
        self.grid = grid
        self.reinit_round()

    def reinit_round(self):
        self.next_figure = self.random_figure()
        size = self.grid.size
        self.placed_cells = [
            [None for y in range(size[1])] for x in range(size[0])]
        self.take_next_figure()
        self.score = 0
        self.last_active = time.time()
        self.pause_status = False
        self.status = "game_active"



    def pause_toggle(self):
        self.pause_status = not self.pause_status
        self.last_active = time.time()

    def random_figure(self):
        fig_i = random.randint(0, len(FIGURES) - 1)
        rot_i = random.randint(0, 4 - 1)
        return FIGURES[fig_i][rot_i]

    def take_next_figure(self):
        '''Replaces current figure with new next random'''
        next_figure = self.random_figure()
        figure_pos = (
            (self.grid.size[0] - len(self.next_figure)) // 2, 0)
        if self.collides(next_figure,figure_pos):
            raise TetrisGameOver
        self.current_figure = self.next_figure
        self.next_figure = next_figure
        self.figure_pos = figure_pos

    def rotation_move(self):
        '''Rotates current figure'''
        new_figure = rotate_figure(self.current_figure)
        if self.collides(new_figure,self.figure_pos):
            return False
        else:
            self.current_figure = new_figure
            return True
    def side_move(self,dir):
        self.move((dir,0))

    def collides(self, figure, pos):
        '''Checks collision of figure at the position (pos) with the occupied cells'''
        for i in range(len(figure)):
            for j in range(len(figure[0])):
                if figure[i][j] != " ":
                    in_range_i = (pos[0] + i >= 0) and (pos[0] + i < self.grid.size[0])
                    in_range_j = (pos[1] + j >= 0) and (pos[1] + j < self.grid.size[1])
                    if (not in_range_i) or (not in_range_j) or self.placed_cells[pos[0] + i][pos[1] + j]:
                        return True
        return False

    def make_next_step(self):
        def get_full_line():
            for j in range(len(self.placed_cells[0])):
                full = True
                for i in range(len(self.placed_cells)):
                    if not self.placed_cells[i][j]:
                        full = False
                if full:
                    return j
            return None

        def remove_line(line_num):
            for i in range(len(self.placed_cells)):
                self.placed_cells[i][0] = None
                for j in range(line_num - 1,0,-1):
                    self.placed_cells[i][j + 1] = self.placed_cells[i][j]

        def remove_full_lines():
            full_lines = 0
            while True:
                line_num = get_full_line()
                if line_num is None:
                    break
                full_lines += 1
                remove_line(line_num)
            self.score += full_lines * (full_lines + 1) * 50

        def place_piece(figure, pos):
            for i in range(len(figure)):
                for j in range(len(figure[0])):
                    if figure[i][j] != " ":
                        self.placed_cells[pos[0] + i][pos[1] + j] = color

        color = self.cell_color
        if not self.move((0, 1)):
            place_piece(self.current_figure, self.figure_pos)
            remove_full_lines()
            self.take_next_figure()

    def move(self, dir):
        new_pos = (self.figure_pos[0] + dir[0], self.figure_pos[1] + dir[1])
        if self.collides(self.current_figure, new_pos):
            return False
        else:
            self.figure_pos = new_pos
            return True

    def propagate(self):
        '''Handles time, gamestatuses and calls model update'''
        c_time = time.time()
        if self.status == "game_active" and (not self.pause_status):
           try:
               if self.last_active + self.move_delay < c_time:
                   self.last_active += self.move_delay
                   self.make_next_step()
           except TetrisGameOver:
               self.status = "game_over"
        elif self.status == "game_over":
            self.reinit_round()

    def draw(self):
        for i in range(len(self.placed_cells)):
            for j in range(len(self.placed_cells[0])):
                if(self.placed_cells[i][j]):
                    self.grid.set_cell_state((i, j), self.placed_cells[i][j])

        for i in range(len(self.current_figure)):
            for j in range(len(self.current_figure[1])):
                if(self.current_figure[i][j] != " "):
                    self.grid.set_cell_state(
                        (self.figure_pos[0] + i, self.figure_pos[1] + j), self.cell_color)


class TetrisGame:
    fontface = "monospace"
    fontsize = 24
    fontcolor = Color("#101010")
    background_color = Color("#808080")

    def __init__(self, screen):
        self.screen = screen
        self.background = pygame.Surface(screen.get_size())
        self.background = self.background.convert()
        self.background.fill(self.background_color)
        self.grid = Grid((10, 20), 15, 1, (20, 10))
        self.game = TetrisModel(self.grid)
        self.score = Score((300, 10), 8, self.fontface,
                           self.fontsize, self.fontcolor)
        self.running = True
        font = pygame.font.SysFont(self.fontface, self.fontsize)
        self.pause_surf = font.render("Paused", 1, self.fontcolor)

    def draw_pause_screen(self):
        '''Shows pause status if paused'''
        if self.game.pause_status:
            self.screen.blit(self.pause_surf, (350, 300))

    def update(self):
        '''Handles input and SnakeModel, Score update'''
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if self.game.status == "game_active":
                    if event.key == K_UP or event.key == K_w:
                        self.game.rotation_move()
                    if event.key == K_LEFT or event.key == K_a:
                        self.game.side_move(-1)
                    if event.key == K_RIGHT or event.key == K_d:
                        self.game.side_move(1)
                    if event.key == K_SPACE or event.key == K_p:
                        self.game.pause_toggle()

        self.game.propagate()
        self.score.set(self.game.score)

    def draw(self):
        '''Draws game objects on screen'''
        self.screen.blit(self.background, (0, 0))
        self.score.draw(self.screen)
        self.grid.clear()
        self.game.draw()
        self.draw_pause_screen()
        self.grid.draw(self.screen)


def main():
    pygame.init()
    screen = pygame.display.set_mode((650, 350))
    pygame.display.set_caption("Tetris")
    game = TetrisGame(screen)
    clock = pygame.time.Clock()

    while game.running:
        clock.tick(60)
        game.update()
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
