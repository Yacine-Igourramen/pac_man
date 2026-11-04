import os
import sys
from ghosts import Ghost, ghost

maze_gen_path = os.path.join(os.path.dirname(__file__), "mazegenerator-00001", "mazegenerator-2.1.0-py3-none-any")
if os.path.exists(maze_gen_path) and maze_gen_path not in sys.path:
    sys.path.insert(0, maze_gen_path)

from mazegenerator import MazeGenerator
import pyglet
from pyglet import shapes
from pyglet.math import Mat4
from pyglet.window import key
from enum import Enum, auto
from parser import parser, Config
import time


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSE = auto()
    GAME_OVER = auto()

## the maze stuff
class maze_assets():
    def __init__(self, maze, size, width, height):
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
        image_path = os.path.join(os.path.dirname(__file__), "floor.png")
        image = pyglet.image.load(image_path)
        ## a lot of calculations are happening below
        w_cells = len(maze[0])
        h_cells = len(maze)
        w_start = (width-(w_cells*size))//2
        h_start = (height-(h_cells*size))//2
        for c, line in enumerate(maze):
            for i, cell in enumerate(line):
                ## we fill the translator with the coodinates the player can be in
                self.translator[(c, i)] = (w_start + i * size, h_start + c * size)
        self.ghost = Ghost((0, 0), self.translator, maze, size, self.main_batch, group=self.ghost_group)
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
                    self.objects.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start+size, i*size+w_start+size, c*size+h_start+size, color=(255, 25, 255, 255), batch=self.main_batch, group=self.maze_group, thickness=7))
                if cell & 2 :
                    self.objects.append(pyglet.shapes.Line(i*size+w_start+size, c*size+h_start+size, i*size+w_start+size, c*size+h_start, color=(255, 25, 255, 255), batch=self.main_batch, group=self.maze_group, thickness=7))
                if cell & 4 :
                    self.objects.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start, i*size+w_start+size, c*size+h_start, color=(255, 25, 255, 255), batch=self.main_batch, group=self.maze_group, thickness=7))
                if cell & 8 :
                    self.objects.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start, i*size+w_start, c*size+h_start+size, color=(255, 25, 255, 255), batch=self.main_batch, group=self.maze_group, thickness=7))
                ## here we fill the pac-gums dictionary
                if cell != 15:
                    self.pac_gums[(c, i)] = pyglet.shapes.Circle((w_start+i*size)+size//2, (h_start+c*size)+size//2, size//14, color=(25, 255, 25, 255), batch=self.main_batch, group=self.maze_group)    


## the player object that hold all the data the player needs to function
class player():
    def __init__(self, health, maze: maze_assets):
        self.name = "pac man"  ## a name idk why i added it
        self.health = health  ## health i guess idk
        self.batch = pyglet.graphics.Batch() ## a batch to make rendering more effecient
        self.maze = maze.maze ## the actual maze as a double list of int
        self.pac_gums = maze.pac_gums  ## this is a dictionary that holds the coordinates and the corresponding pac_gum
        self.direction = None  ## the direction where pac_man/women is currentely moving
        self.tmp_dir = None  ## the movement queue
        self.cell = (0, 0) ## his/her current cell
        self.set_player() ## a function to set the player in the middle of the maze
        self.translator = maze.translator ## this is a dictionary that translate the current cell into screen coordinates
        self.cord = self.translator[self.cell] ## we're translating the cell we set a 2 lines ago to screen coordinates (look above)
        self.old_cord = (0, 0) ## this is used during movement read the move() function for more info
        self.score = 0 ## looks like the score
        self.mid_move = False ## a flag to know if we reached the wanted cell or not yet
        self.score_obj = pyglet.text.Label(
                            text=f'score = {self.score}',
                            font_name=None,
                            font_size=50,
                            italic=False,
                            color=(255, 255, 255, 255),
                            x=10,
                            y=10,                         ## score text
                            width=None,
                            height=None,
                            anchor_x='left',
                            anchor_y='baseline',
                            align='left',
                            multiline=False,
                            batch=self.batch
                        )
        self.dt_update = pyglet.text.Label(
                            text=f'score = {self.score}',
                            font_name=None,
                            font_size=50,
                            italic=False,
                            color=(255, 255, 255, 255),
                            x=500,
                            y=10,
                            width=None,
                            height=None,
                            anchor_x='left',
                            anchor_y='baseline',
                            align='left',
                            multiline=False,
                            batch=self.batch
                        )
        self.rendering = pyglet.text.Label(
                            text=f'score = {self.score}',
                            font_name=None,
                            font_size=50,
                            italic=False,
                            color=(255, 255, 255, 255),
                            x=10,
                            y=900,
                            width=None,
                            height=None,
                            anchor_x='left',
                            anchor_y='baseline',
                            align='left',
                            multiline=False,
                            batch=self.batch
                        )
        ## u changed what's below before so u know
        image_path = os.path.join(os.path.dirname(__file__), "player.png")
        sheet = pyglet.image.load(image_path)
        grid = pyglet.image.ImageGrid(sheet, 4, 4)

        # resting stances (first column for each row):
        # from toop to bottom:
        # row 1 (top, grid row 3): front view
        # row 2 (grid row 2): back view
        # row 3 (grid row 1): left view
        # row 4 (bottom, grid row 0): right view
        self.resting_stances = {
            "down": grid[3, 0].get_texture(),
            "up": grid[2, 0].get_texture(),
            "left": grid[1, 0].get_texture(),
            "right": grid[0, 0].get_texture(),
        }
        frame_duration = 0.1  # 100ms per frame
        self.animations = {
            "down": pyglet.image.Animation.from_image_sequence([grid[3, c] for c in range(4)], duration=frame_duration, loop=True),
            "up": pyglet.image.Animation.from_image_sequence([grid[2, c] for c in range(4)], duration=frame_duration, loop=True),
            "left": pyglet.image.Animation.from_image_sequence([grid[1, c] for c in range(4)], duration=frame_duration, loop=True),
            "right": pyglet.image.Animation.from_image_sequence([grid[0, c] for c in range(4)], duration=frame_duration, loop=True),
        }
        # Start game in resting stance (front view)
        self.object = pyglet.sprite.Sprite(self.resting_stances["down"], x=self.cord[0], y=self.cord[1], batch=self.batch)
        self.object.scale = maze.size / self.resting_stances["down"].width

    def update_animation(self, moving=False):
        dir_key = self.direction if self.direction in self.animations else "down"
        target = self.animations[dir_key] if moving else self.resting_stances[dir_key]
        if self.object.image is not target:
            self.object.image = target

    ## its in the name of the function
    def change_maze(self, maze: maze_assets):
        self.direction = None ## we have to stop movement
        self.mid_move = False
        self.maze = maze.maze ## we change the maze
        self.pac_gums = maze.pac_gums ## the pac_gums too
        self.set_player()
        self.translator = maze.translator ## the coordinates translator too
        ## u know the rest
        self.cord = self.translator[self.cell]
        self.object.scale = maze.size / self.resting_stances["down"].width
        self.object.x = self.cord[0]
        self.object.y = self.cord[1]
        self.update_animation(moving=False)

    # this function used to be long
    def set_cord(self):
        self.old_cord = self.cord
        self.cord = self.translator[self.cell]

    # puts the player in the middle
    def set_player(self):
        self.cell = (len(self.maze)//2, len(self.maze[0])//2) # we devide the maze and if the mid point is a closed cell we move 1 cell to the left
        if self.maze[self.cell[0]][self.cell[1]] == 15:
            self.cell = (self.cell[0], self.cell[1]-1)
        self.pac_gums[self.cell].delete()
        self.pac_gums[self.cell] = None
        self.maze[self.cell[0]][self.cell[1]] = self.maze[self.cell[0]][self.cell[1]] ^ 16

    ## basically moves the player on the screen by the amount of pixels equal to distance
    def move(self):
        distance = 2 ## how many pixels to move by each call still needs tweaking

        x = self.old_cord[0]
        y = self.old_cord[1] ## we save where the player used to be

        ## below we move the player basec on where the new location is relative to the old one
        if self.cord[0] > x:
            x = min(x + distance, self.cord[0]) 
        elif self.cord[0] < x:
            x = max(x - distance, self.cord[0])

        if self.cord[1] > y:
            y = min(y + distance, self.cord[1])
        elif self.cord[1] < y:
            y = max(y - distance, self.cord[1])
        ## this is why we save the old ones

        self.old_cord = (x, y)
        self.object.x = x
        self.object.y = y

        ## below the moment we reach the new location we check the 16th bit in the maze for the pac_gum and eat it
        if self.old_cord == self.cord:
            self.mid_move = False
            if self.pac_gums[self.cell] is not None:
                self.score += 10
                self.score_obj.text = f"score = {self.score}"
                self.pac_gums[self.cell].delete()
                self.pac_gums[self.cell] = None
                self.maze[self.cell[0]][self.cell[1]] = self.maze[self.cell[0]][self.cell[1]] ^ 16

    ## we take a direction and check if its valid based on the curent location in the maze if not we put it in the queue
    def set_direction(self, Direction):
        box = self.maze[self.cell[0]][self.cell[1]]
        if Direction == "up":
            if box & 1 == 0:
                self.direction = "up"
                self.tmp_dir = None
            else:
                self.tmp_dir = "up"
        if Direction == "right":
            if box & 2 == 0:
                self.direction = "right"
                self.tmp_dir = None
            else:
                self.tmp_dir = "right"
        if Direction == "down":
            if box & 4 == 0:
                self.direction = "down"
                self.tmp_dir = None
            else:
                self.tmp_dir = "down"
        if Direction == "left":
            if box & 8 == 0:
                self.direction = "left"
                self.tmp_dir = None
            else:
                self.tmp_dir = "left"
        self.update_animation(moving=self.mid_move)

    ## this one make the movement happen after it checks again for some reason anyway i'il see to it later its 5:40 rn
    def move_player(self):
        ##if we're mid movement no need to check all of this again
        if self.mid_move:
            self.move()
            return
        box = self.maze[self.cell[0]][self.cell[1]]
        ## the queue direction has piority
        if self.tmp_dir == "up" and box & 1 == 0:
            self.direction = self.tmp_dir
            self.tmp_dir = None
        elif self.tmp_dir == "right" and box & 2 == 0:
            self.direction = self.tmp_dir
            self.tmp_dir = None
        elif self.tmp_dir == "down" and box & 4 == 0:
            self.direction = self.tmp_dir
            self.tmp_dir = None
        elif self.tmp_dir == "left" and box & 8 == 0:
            self.direction = self.tmp_dir
            self.tmp_dir = None

        ## in here we change the cell and make the movement happen
        if self.direction == "up" and box & 1 == 0:
            self.cell = (self.cell[0] + 1, self.cell[1])
        elif self.direction == "right" and box & 2 == 0:
            self.cell = (self.cell[0], self.cell[1] + 1)
        elif self.direction == "down" and box & 4 == 0:
            self.cell = (self.cell[0] - 1, self.cell[1])
        elif self.direction == "left" and box & 8 == 0:
            self.cell = (self.cell[0], self.cell[1] - 1)
        else:
            self.update_animation(moving=False)
            return
        ## we only set the new coordinates after a movement is valid otherwise we exit
        self.set_cord()
        self.mid_move = True
        self.update_animation(moving=True)

## the menu screen and its 2 texts
class menu_screen():
    def __init__(self, screen_w, screen_h):
        self.menu_batch = pyglet.graphics.Batch()
        self.txt = []
        self.txt.append(pyglet.text.Label(text="PAC-MAN", font_size=100, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))
        self.txt.append(pyglet.text.Label(text="press ENTER to start", font_size=20, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2-300, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))
        self.txt.append(pyglet.text.Label(text="press ESCAPE to exit", font_size=20, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2-350, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))
        


class Pause_screen():
    def __init__(self,screen_w, screen_h):
        self.pause_batch = pyglet.graphics.Batch()
        self.assets = []
        self.assets.append(pyglet.shapes.Rectangle(x=0, y=0, width=screen_w, height=screen_h, color=(0, 0, 0), batch=self.pause_batch))
        self.assets[-1].opacity = 150
        self.assets.append(pyglet.shapes.Rectangle(x=screen_w//4, y=screen_h//4, width=screen_w//2, height=screen_h//2, color=(0, 0, 0), batch=self.pause_batch))
        self.assets.append(pyglet.text.Label(text=f'paused', font_name=None,font_size=50, color=(255, 255, 255, 255),x=screen_w/2-150,y=screen_h//2+50,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.pause_batch))
        self.assets.append(pyglet.text.Label(text=f'press p to continue', font_name=None,font_size=20, color=(255, 255, 255, 255),x=screen_w/2-100,y=screen_h//2,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.pause_batch))
        self.assets.append(pyglet.text.Label(text=f'press R to restart', font_name=None, font_size=20, color=(255, 255, 255, 255),x=screen_w/2-100,y=screen_h//2-50,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.pause_batch))
        self.assets.append(pyglet.text.Label(text=f'press ESCAPE to exit', font_name=None, font_size=20, color=(255, 255, 255, 255),x=screen_w/2-100,y=screen_h//2-100,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.pause_batch))


## this is the window class
class GameWindow(pyglet.window.Window):
    def __init__(self, info, health):
        super().__init__(fullscreen=True, vsync=False)
        self.state = GameState.MENU
        self.info = info
        self.lvl = 0
        self.health = health
        self.game_play = None ## this is the maze class
        self.menu = menu_screen(info[0][2], info[0][3]) ## this is the menu as the name say
        self.pause = Pause_screen(info[0][2], info[0][3])
        self.player = None ## the player exists seperately from the maze
        self.ghost_timer = 0.0 ## ***** added this pretty self explanatory
        pyglet.clock.schedule_interval(self.update, 1/(info[0][1]*2.5)) ## the refresh rate 

    ## the function that writes to the window with its 3 options
    def on_draw(self):
        start = time.perf_counter()
        self.clear()
        if self.state == GameState.MENU:
            self.menu.menu_batch.draw()
        elif self.state == GameState.PLAYING:
            self.game_play.main_batch.draw()
            self.player.batch.draw()
            elapsed = (time.perf_counter() - start) * 1000
            self.player.rendering.text = f"Draw time: {elapsed:.2f} ms"
        elif self.state == GameState.PAUSE:
            self.game_play.main_batch.draw()
            self.player.batch.draw()
            self.pause.pause_batch.draw()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

    def draw_game_over(self):
        self.menu.menu_batch.draw()
        
    ## this one handeles key presses
    def on_key_press(self, symbol, modifiers):
        if self.state == GameState.PLAYING:
            if symbol == key.W or symbol == key.UP:
                self.player.set_direction("up")
            if symbol == key.D or symbol == key.RIGHT:
                self.player.set_direction("right")
            if symbol == key.S or symbol == key.DOWN:
                self.player.set_direction("down")
            if symbol == key.A or symbol == key.LEFT:
                self.player.set_direction("left")
            ## press p to pause the game
            if symbol == key.P or symbol == key.ESCAPE:
                self.state = GameState.PAUSE
        elif self.state == GameState.PAUSE:
            ## repress it to continue
            if symbol == key.P:
                self.state = GameState.PLAYING
            if symbol == key.R:
                self.game_play = maze_assets(self.info[self.lvl][0], self.info[self.lvl][1], self.info[self.lvl][2], self.info[self.lvl][3])
                self.player.change_maze(self.game_play)
                self.state = GameState.PLAYING
            if symbol == key.ESCAPE:
                self.game_play = None
                self.state = GameState.MENU
        elif self.state == GameState.MENU:
            if symbol == key.ENTER:
                self.game_play = maze_assets(self.info[0][0], self.info[0][1], self.info[0][2], self.info[0][3])
                self.player = player(self.health, maze=self.game_play)
                self.state = GameState.PLAYING
            if symbol == key.ESCAPE:
                self.state = self.close()

    ## this is the one that get's called many times a second
    def update(self, dt):
        fps = 1 / dt if dt > 0 else 0
        if self.state == GameState.PLAYING:
            self.player.dt_update.text = f"Update FPS: {fps:.1f} | dt: {dt * 1000:.2f} ms"
            ## we move the player which gives us continues movement
            self.player.move_player()
            ## move the ghost towards player on a timer
            self.ghost_timer += dt
            if self.ghost_timer >= 0.25:
                self.ghost_timer = 0.0
                if self.game_play and self.player:
                    self.game_play.ghost.move_ghost(self.player.cell)
            ## below i check if all the pac-gums are eaten then i move to the next lvl
            if all(value is None for value in self.player.pac_gums.values()):
                self.lvl += 1
                if self.lvl < len(self.info):
                    self.game_play = maze_assets(self.info[self.lvl][0], self.info[self.lvl][1], self.info[self.lvl][2], self.info[self.lvl][3])
                    self.player.change_maze(self.game_play)
                    pyglet.clock.unschedule(self.update)
                    pyglet.clock.schedule_interval(self.update, 1/(self.info[self.lvl][1]*2.5))
                else:
                    self.state = GameState.MENU
        elif self.state == GameState.MENU:
            pass

## this one only detects the screen size to make the maze dynamic
def size_detector(maze):
    display = pyglet.display.get_display()
    screen = display.get_default_screen()
    screen_width = screen.width
    screen_height = screen.height
    ####
    w_cells = len(maze[0])
    h_cells = len(maze)
    maze.reverse()
    ## all the cells are squares so we take the smaller side and make it the size o the square
    size = (screen_width)//w_cells if (screen_width)//w_cells < (screen_height-100)//h_cells else (screen_height-100)//h_cells
    print(size)
    return [maze, size, screen_width, screen_height]


def main():
    if len(sys.argv) == 1:
        sys.argv.append("config.json")
    conf = parser(sys.argv)
    mazes = []
    ## we generate all the mazes
    for j, i in enumerate(conf.levels):
        mazes.append(MazeGenerator(size=(i["width"], i["height"])))
        ## only the first one uses the seed
        if j == 0:
            mazes[-1].generate(conf.seed)
        else:
            mazes[-1].generate()
    info = []
    ## we fill ino with the data each maze needs
    for i in mazes:
        info.append(size_detector(i.maze))
    ## we make the window
    win = GameWindow(info, conf.lives)

    pyglet.app.run()


if __name__ == "__main__":
    main()
