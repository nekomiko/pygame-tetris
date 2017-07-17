import pygame
from pygame.locals import *


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
