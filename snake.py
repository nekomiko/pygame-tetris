import pygame
from pygame.locals import *


from grid import Grid
import time, random
class SnakeCollision(Exception):
    pass

class Snake:
    '''Snake object'''
    cell_color = "#FF00FF"
    collectible_color = "#00FF00"
    def __init__(self,grid_o,length=3,startpos=(-1,-1)):
        '''self.grid: Grid where Snake moves
        self.body_cells: array of coordinates of cells composing snake body
        self.score: current score
        self.direction: vector of snake direction
        self.last_active: unix-time of the last move
        self.move_delay: delay between moves in ms
        self.expanding: number of moves left which increasing size of snake'''
        if(startpos == (-1,-1)):
            startpos = ( grid_o.size[0] // 2, grid_o.size[1] // 2)
        self.grid = grid_o
        self.body_cells = [ (startpos[0]-i,startpos[1]) for i in range(0,length) ]
        self.score = 0
        self.direction = (1,0)
        self.last_active = time.time()
        self.move_delay = 0.250
        self.expanding = 0
        self.collectibles = []
        self.place_new_collectible()
    def place_new_collectible(self):
        if len(self.body_cells) >= self.grid.size[0] * self.grid.size[1]:
            return None
        while True:
            cell = (random.choice(range(self.grid.size[0])),
                    random.choice(range(self.grid.size[0])))
            if not (cell in self.body_cells):
                self.collectibles.append(cell)
                return cell

    def make_next_step(self):
        def pos_sum(pos1,pos2):
            x1,y1 = pos1
            x2,y2 = pos2
            return (x1+x2,y1+y2)
        next_cell = pos_sum(self.body_cells[0],self.direction)
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

        #check for collisions
        if next_cell in self.body_cells[:-1]:
            raise SnakeCollision
        if next_cell[0] < 0 or next_cell[0] >= self.grid.size[0] or \
                next_cell[1] < 0 or next_cell[1] >= self.grid.size[1]:
            raise SnakeCollision

        self.body_cells = new_cells_list

    def set_direction(self,new_direction):
        x,y = new_direction
        if(x < -1 or y < -1 or x > 1 or y > 1 or ((x+y) != 1 and (x+y) != -1)):
            return False
        '''If direction is the same do nothing'''
        if(self.direction == new_direction):
            return False
        '''If direction is reverse do nothing'''
        if(self.direction[0] + new_direction[0] == 0 and \
           self.direction[1] + new_direction[1] == 0):
            return False
        self.direction = new_direction
        return True

    def propagate(self):
        c_time = time.time()
        steps = int((c_time - self.last_active) / self.move_delay)
        for i in range(0,steps):
            self.last_active += self.move_delay
            self.make_next_step()

    def draw(self,screen):
        self.grid.clear()
        for c in self.body_cells:
            self.grid.set_cell_state(c,self.cell_color)
        for c in self.collectibles:
            self.grid.set_cell_state(c,self.collectible_color)
        self.grid.draw(screen)

def main():
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    pygame.display.set_caption("Snake")
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(Color("#808080"))
    screen.blit(background,background.get_rect())
    grid = Grid((30,30),10,1,(20,10))
    grid.cell_data[0][0] = grid.active_color
    snake = Snake(grid)

    screen.blit(grid.image, grid.rect)
    pygame.display.flip()

    clock = pygame.time.Clock()
    running = True
    counter = 0
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_UP or event.key == K_w:
                    snake.set_direction((0,-1))
                if event.key == K_DOWN or event.key == K_s:
                    snake.set_direction((0,1))
                if event.key == K_LEFT or event.key == K_a:
                    snake.set_direction((-1,0))
                if event.key == K_RIGHT or event.key == K_d:
                    snake.set_direction((1,0))

        snake.propagate()
        snake.draw(screen)
        pygame.display.flip()

if __name__ == "__main__": main()






