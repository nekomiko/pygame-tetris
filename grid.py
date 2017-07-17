import pygame
from pygame.locals import *


class Grid:
    '''Grid object, representing colored grid
       with ability to draw it on Surface
   '''
    empty_color = "#FFFFFF"
    border_color = "#404040"
    active_color = "#FF00FF"

    def __init__(self, size, cell_size=10, cell_border=1, topleft=(0, 0)):
        '''size: (width , height) dimensions of grid in cellsi
        cell_size: size of side of cell
        cell_border: border size of outline of cells
                     including grid's outer borderi
        topleft: (x,y) coordinates of top left corner
        self.image: Surface-object containing visual representation of grid
                after calling an self.update() method
        self.rect: rectangular, containing Grid

        self.cell_data: 2d-array with self.size dimensions containing
                        colors of Grid's cells in "#XXXXXX" format

        self._cell_surfaces: 2d-array with self.size dimension containing
                             colored surfaces of corresponding colors

        self._cell_rects: 2d-array with self.size dimensions containing
                          rectangles of cells (in self.image coordinates)


        '''
        self.size = size
        self.cell_size = cell_size
        self.cell_border = cell_border
        surface_width = self.size[0] * (self.cell_size + self.cell_border) + \
            self.cell_border
        surface_height = self.size[1] * (self.cell_size + self.cell_border) + \
            self.cell_border
        self.image = pygame.Surface((surface_width, surface_height))
        self.image.fill(Color(self.border_color))
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        self.cell_data = [
            [None for y in range(size[1])] for x in range(size[0])]
        self._cell_surfaces = [[pygame.Surface((self.cell_size, self.cell_size))
                                for y in range(size[1])] for x in range(size[0])]
        self._cell_rects = [[self._cell_coord_to_rect(x, y) for y in range(size[1])]
                            for x in range(size[0])]
        self.update()

    def _cell_coord_to_rect(self, n, m):
        '''Converts (column,row) coordinates of cell to Rect'''
        return Rect((self.cell_border * (n + 1) + self.cell_size * n,
                     self.cell_border * (m + 1) + self.cell_size * m),
                    (self.cell_size, self.cell_size))

    def _draw_cell_surfaces(self):
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                color = self.cell_data[x][y] if self.cell_data[x][y] else self.empty_color
                self._cell_surfaces[x][y].fill(Color(color))
                self.image.blit(
                    self._cell_surfaces[x][y], self._cell_rects[x][y])

    def update(self):
        '''Redraw self.image'''
        self._draw_cell_surfaces()

    def abs_coord_to_cell(self, pos):
        '''Takes absolute display coordinates and
        gives cell(column,row) containing them'''
        def in_range(n, m, x):
            return n <= x <= m
        x, y = pos
        x -= self.rect.left + (self.cell_border // 2)
        y -= self.rect.top + (self.cell_border // 2)
        bordered_cell = self.cell_border + self.cell_size
        retpos = (x // bordered_cell, y // bordered_cell)
        if in_range(0, self.size[0], retpos[0]) and in_range(0, self.size[1], retpos[1]):
            return retpos
        else:
            return None

    def set_cell_state(self, pos, color_str):
        '''Sets color of the cell with `pos` coordinated
        pos: 2-tuple (c,r)
        color_str: color in #XXXXXX format'''
        x, y = pos
        self.cell_data[x][y] = color_str

    def get_cell_state(self,pos):
        x ,y = pos
        return self.cell_data[x][y]

    def get_size(self):
        return self.size

    def flip_color(self, pos):
        '''Flips color in cell with pos (colomun,row) coordinates'''
        x, y = pos
        if(self.cell_data[x][y]):
            self.cell_data[x][y] = None
        else:
            self.cell_data[x][y] = self.active_color

    def clear(self):
        '''Clears self.cell_data inplace'''
        for x in range(self.size[0]):
            for y in range(self.size[1]):
                self.cell_data[x][y] = None

    def draw(self, screen):
        '''Draws grid on screen'''
        self.update()
        screen.blit(self.image, self.rect)


def main():
    '''Click-cell-to-activate interactive demo'''
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Test Grid")
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(Color("#808080"))
    screen.blit(background, background.get_rect())
    grid = Grid((20, 20), 10, 1, (20, 10))
    grid.cell_data[0][0] = grid.active_color

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
            elif event.type == MOUSEBUTTONDOWN:
                pos = grid.abs_coord_to_cell(pygame.mouse.get_pos())
                if pos:
                    grid.flip_color(pos)
        grid.draw(screen)
        pygame.display.flip()


if __name__ == "__main__":
    main()
