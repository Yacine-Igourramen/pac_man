from ghosts import Ghost
import pyglet
from pyglet import shapes
from pyglet.math import Mat4
import os
from enum import Enum, auto
import random


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSE = auto()
    WIN = auto()
    GAME_OVER = auto()

## the maze stuff
class maze_assets():
    def __init__(self, maze, size, width, height, num_pac_gum):
        ## a special batch
        self.main_batch = pyglet.graphics.Batch()
        ## groups to control draw order (floor below walls and pacgums)
        self.floor_group = pyglet.graphics.Group(order=0)
        self.maze_group = pyglet.graphics.Group(order=1)
        self.ghost_group = pyglet.graphics.Group(order=2)
        ## this dictionary is gonna be used by the player to translate their position from a maze cell to screen coordinates
        self.translator = {}
        ## and this one holds the cell and the corresponding pac-gum
        self.pac_gums = {}
        ## just a list to hold the maze drawings
        self.objects = []
        ## the maze because the player needs it even tho its not used here
        self.maze = maze
        self.size = size
        ## ★★★ store screen dimensions for placing indicators
        self.width = width
        self.height = height
        image_path = os.path.join(os.path.dirname(__file__), "floor.png")
        image = pyglet.image.load(image_path)
        ## a lot of calculations are happening below
        w_cells = len(maze[0])
        h_cells = len(maze)
        w_start = (width-(w_cells*size))//2
        h_start = (height-(h_cells*size))//2
        randomiser = []
        for c, line in enumerate(maze):
            for i, cell in enumerate(line):
                ## we fill the translator with the coodinates the player can be in
                self.translator[(c, i)] = (w_start + i * size, h_start + c * size)
                if cell != 15:
                    randomiser.append((c, i))
        random.shuffle(randomiser)
        randomiser = randomiser[:num_pac_gum]
        ## ★★★ 4 ghosts in each corner
        ghost_configs = [
            # ((h_cells - 1, 0), (255, 0, 0, 255)),            ## ★★★ top left
            # ((h_cells - 1, w_cells - 1), (255, 184, 255, 255)),  ## ★★★ top right
            # ((0, 0), (0, 255, 255, 255)),                    ## ★★★ bottom left
            # ((0, w_cells - 1), (255, 184, 82, 255)),         ## ★★★ bottom rright
        ]
        ## ★★★ list holding all 4 ghosts
        self.ghosts = []
        for corner, color in ghost_configs:
            self.ghosts.append(Ghost(corner, self.translator, maze, size, self.main_batch, color=color, group=self.ghost_group))
        for cord in self.translator.values():
            ## we use the same player coordinates to fill the floor of the cell
            self.objects.append(pyglet.sprite.Sprite(image, x=cord[0], y=cord[1], batch=self.main_batch, group=self.floor_group))
            ## and scale it accordingly 
            self.objects[-1].scale = size / image.width
        ## we added the floors first now the walls so they're above them
        for c, line in enumerate(maze):
            for i, cell in enumerate(line):
                ## just checking the bit and drawing the wall based on the size
                if cell & 1 :
                    self.objects.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start+size, i*size+w_start+size, c*size+h_start+size, color=(255, 255, 255, 255), batch=self.main_batch, group=self.maze_group, thickness=40))
                if cell & 2 :
                    self.objects.append(pyglet.shapes.Line(i*size+w_start+size, c*size+h_start+size, i*size+w_start+size, c*size+h_start, color=(255, 255, 255, 255), batch=self.main_batch, group=self.maze_group, thickness=40))
                if cell & 4 :
                    self.objects.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start, i*size+w_start+size, c*size+h_start, color=(255, 255, 255, 255), batch=self.main_batch, group=self.maze_group, thickness=40))
                if cell & 8 :
                    self.objects.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start, i*size+w_start, c*size+h_start+size, color=(255, 255, 255, 255), batch=self.main_batch, group=self.maze_group, thickness=40))
                ## here we fill the pac-gums dictionary
                if (c, i) in randomiser:
                    self.pac_gums[(c, i)] = pyglet.shapes.Circle((w_start+i*size)+size//2, (h_start+c*size)+size//2, size//14, color=(255, 25, 25, 255), batch=self.main_batch, group=self.maze_group)    
                else:
                    self.pac_gums[(c, i)] = None