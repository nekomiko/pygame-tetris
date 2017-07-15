import pygame
from pygame.locals import *


from grid import Grid
import time
import random


class SnakeCollision(Exception):
    pass


class SnakeModel:
    '''Snake object
    self.status values:
        game_active
        game_over'''

    cell_color = "#FF00FF"
    collectible_color = "#00FF00"

    def __init__(self, grid_o, length=3, startpos=(-1, -1)):
        '''self.grid: Grid where Snake moves
        self.body_cells: array of coordinates of cells composing snake body
        self.score: current score
        self.direction: vector of snake direction
        self.last_active: unix-time of the last move
        self.move_delay: delay between moves in ms
        self.expanding: number of moves left which increasing size of snake'''
        if(startpos == (-1, -1)):
            startpos = (grid_o.size[0] // 2, grid_o.size[1] // 2)
        self.length = length
        self.startpos = startpos
        self.grid = grid_o
        self.move_delay = 0.250
        self.gameover_blink_delay = 0.1
        self.gameover_blinks = 10
        self.reinit_round()

    def reinit_round(self):
        '''Reinitialization of game after start or gameover'''
        self.score = 0
        self.body_cells = [(self.startpos[0] - i, self.startpos[1])
                           for i in range(0, self.length)]
        self.score = 0
        self.direction = QueuedValue((1, 0))
        self.last_active = time.time()
        self.expanding = 0
        self.collectibles = []
        self.place_new_collectible()
        self.status = "game_active"
        self.blink_status = True
        self.blinks_made = 0
        self.pause_status = False

    def pause_toggle(self):
        self.pause_status = not self.pause_status
        self.last_active = time.time()
        # if self.status == "game_active":
        #    self.status = "game_paused"
        # elif self.status == "game_paused":
        #    self.status == "game_active"

    def place_new_collectible(self):
        '''Places snake body piece at random location'''
        if len(self.body_cells) >= self.grid.size[0] * self.grid.size[1]:
            return None
        while True:
            cell = (random.choice(range(self.grid.size[0])),
                    random.choice(range(self.grid.size[0])))
            if not (cell in self.body_cells):
                self.collectibles.append(cell)
                return cell

    def make_next_step(self):
        '''Updates model: hadles snakes's next move'''
        def pos_sum(pos1, pos2):
            x1, y1 = pos1
            x2, y2 = pos2
            return (x1 + x2, y1 + y2)
        direction = self.direction.get()
        next_cell = pos_sum(self.body_cells[0], direction)
        if next_cell in self.collectibles:
            self.expanding += 1
            self.collectibles.remove(next_cell)
            self.place_new_collectible()
            self.score += 100
        if self.expanding == 0:
            new_cells_list = [next_cell] + self.body_cells[:-1]
        else:
            new_cells_list = [next_cell] + self.body_cells
            self.expanding -= 1

        # check for collisions
        if next_cell in self.body_cells[:-1]:
            raise SnakeCollision
        if next_cell[0] < 0 or next_cell[0] >= self.grid.size[0] or \
                next_cell[1] < 0 or next_cell[1] >= self.grid.size[1]:
            raise SnakeCollision

        self.body_cells = new_cells_list

    def set_direction(self, new_direction):
        '''Changes direction of snake,
        handles validation and opposite direction cases'''
        x, y = new_direction
        if(x < -1 or y < -1 or x > 1 or y > 1 or ((x + y) != 1 and (x + y) != -1)):
            return False
        direction = self.direction.observe()
        '''If direction is the same do nothing'''
        if(direction == new_direction):
            return False
        '''If direction is reverse do nothing'''
        if(direction[0] + new_direction[0] == 0 and
           direction[1] + new_direction[1] == 0):
            return False
        self.direction.set(new_direction)
        return True

    def propagate(self):
        '''Handles time, gamestatuses and calls model update'''
        c_time = time.time()
        if self.status == "game_active" and (not self.pause_status):
            try:
                if self.last_active + self.move_delay < c_time:
                    self.last_active += self.move_delay
                    self.make_next_step()
            except SnakeCollision:
                self.status = "game_over"
        elif self.status == "game_over":
            if self.last_active + self.gameover_blink_delay < c_time:
                self.last_active += self.gameover_blink_delay
                if self.blinks_made >= self.gameover_blinks:
                    self.reinit_round()

                self.blink_status = not self.blink_status
                self.blinks_made += 1

    def draw_body(self):
        '''Draws snake's body cells on the grid'''
        for c in self.body_cells:
            self.grid.set_cell_state(c, self.cell_color)

    def draw(self):
        '''Draws snake and other objects on grid'''
        # Handle blinking after gameover
        if self.status == "game_over":
            if self.blink_status:
                self.draw_body()

        else:
            self.draw_body()
            for c in self.collectibles:
                self.grid.set_cell_state(c, self.collectible_color)


class Score:
    def __init__(self, pos, length, fontface, fontsize, fontcolor):
        '''pos: top left coordinate of score box
        lenght: number of digits in score indicator'''
        self.pos = pos
        self.length = length
        self.fontface = fontface
        self.fontsize = fontsize
        self.fontcolor = fontcolor
        self.font = pygame.font.SysFont(fontface, fontsize)
        self.val = 0

    def set(self, val):
        self.val = val

    def draw(self, screen):
        score_surf = self.font.render(
            "Score: " + str(self.val).zfill(self.length), 1, self.fontcolor)
        screen.blit(score_surf, self.pos)


class SnakeGame:
    fontface = "monospace"
    fontsize = 24
    fontcolor = Color("#101010")
    background_color = Color("#808080")

    def __init__(self, screen):
        self.screen = screen
        self.background = pygame.Surface(screen.get_size())
        self.background = self.background.convert()
        self.background.fill(self.background_color)
        self.grid = Grid((30, 30), 10, 1, (20, 10))
        self.snake = SnakeModel(self.grid)
        self.score = Score((400, 10), 8, self.fontface,
                           self.fontsize, self.fontcolor)
        self.running = True
        self.gameover = False
        font = pygame.font.SysFont(self.fontface, self.fontsize)
        self.pause_surf = font.render("Paused", 1, self.fontcolor)

    def draw_pause_screen(self):
        '''Shows pause status if paused'''
        if self.snake.pause_status:
            self.screen.blit(self.pause_surf, (400, 300))

    def update(self):
        '''Handles input and SnakeModel, Score update'''
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if self.snake.status == "game_active":
                    if event.key == K_UP or event.key == K_w:
                        self.snake.set_direction((0, -1))

                    if event.key == K_DOWN or event.key == K_s:
                        self.snake.set_direction((0, 1))

                    if event.key == K_LEFT or event.key == K_a:
                        self.snake.set_direction((-1, 0))

                    if event.key == K_RIGHT or event.key == K_d:
                        self.snake.set_direction((1, 0))
                    if event.key == K_SPACE or event.key == K_p:
                        self.snake.pause_toggle()

        self.snake.propagate()
        self.score.set(self.snake.score)

    def draw(self):
        '''Draws game objects on screen'''
        self.screen.blit(self.background, (0, 0))
        self.score.draw(self.screen)
        self.grid.clear()
        self.snake.draw()
        self.draw_pause_screen()
        self.grid.draw(self.screen)


class QueuedValue:
    '''Contains a value that can be queued for change or observed or get,
    queued value remains unobservable before get request'''

    def __init__(self, val):
        self.queued = val
        self.val = val

    def set(self, val):
        '''Queue value for change'''
        self.queued = val

    def get(self):
        '''Updates value with queued and returns new'''
        self.val = self.queued
        return self.val

    def observe(self):
        '''Ignores queued value, returns old'''
        return self.val


def main():
    pygame.init()
    screen = pygame.display.set_mode((650, 350))
    pygame.display.set_caption("Snake")
    game = SnakeGame(screen)
    clock = pygame.time.Clock()

    while game.running:
        clock.tick(60)
        game.update()
        game.draw()
        pygame.display.flip()


if __name__ == "__main__":
    main()
