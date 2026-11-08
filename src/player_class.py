import pyglet
from pyglet import shapes
from pyglet.math import Mat4
import os
from pyglet.window import key
from maze import GameState


## the player object that hold all the data the player needs to function
class player():
    def __init__(self, health, maze: maze_assets, costs):
        self.name = "pac man"  ## a name idk why i added it
        self.health = health  ## health i guess idk
        self.batch = pyglet.graphics.Batch() ## a batch to make rendering more effecient
        self.maze = maze.maze ## the actual maze as a double list of int
        self.pac_gums = maze.pac_gums  ## this is a dictionary that holds the coordinates and the corresponding pac_gum
        self.direction = None  ## the direction where pac_man/woman is currentely moving
        self.tmp_dir = None  ## the movement queue
        self.cell = (0, 0) ## his/her current cell
        self.set_player() ## a function to set the player in the middle of the maze
        self.translator = maze.translator ## this is a dictionary that translate the current cell into screen coordinates
        self.cord = self.translator[self.cell] ## we're translating the cell we set a 2 lines ago to screen coordinates (look above)
        self.old_cord = (0, 0) ## this is used during movement read the move() function for more info
        self.score = 0 ## looks like the score
        self.lvl_score = 0
        self.mid_move = False ## a flag to know if we reached the wanted cell or not yet
        self.cost_per_gum = costs[0]
        self.cost_per_super_gum = costs[1]
        self.cost_per_ghost = costs[2]
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
        ## ★★★ lives counter indicator on the top right screen
        self.lives_obj = pyglet.text.Label(
                            text=f'lives = {self.health}',
                            font_name=None,
                            font_size=50,
                            italic=False,
                            color=(255, 255, 255, 255),
                            x=maze.width - 20,
                            y=900,
                            width=None,
                            height=None,
                            anchor_x='right',
                            anchor_y='baseline',
                            align='right',
                            multiline=False,
                            batch=self.batch
                        )
        ## u changed what's below before so u know
        image_path = os.path.join(os.path.dirname(__file__), "player.png")
        sheet = pyglet.image.load(image_path)
        grid = pyglet.image.ImageGrid(sheet, 4, 4)

        # ★★★ resting stances (first column for each row):
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
        # ★★★ to start game in resting stance (front view)
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
        self.score += self.lvl_score
        self.lvl_score = 0
        ## ★★★ update lives indicator position for new maze 
        ## why tho?
        self.score_obj.text = f"score = {self.score+self.lvl_score}"
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
        ## ★★★ only delete pacgum if it has not been eaten yet
        if self.pac_gums.get(self.cell) is not None:
            self.pac_gums[self.cell].delete()
            self.pac_gums[self.cell] = None
            self.maze[self.cell[0]][self.cell[1]] = self.maze[self.cell[0]][self.cell[1]] ^ 16

    ## ★★★ reseting the player to the middle after losing a life i want to add a short "cutsene" to it befor that later
    def reset_position(self):
        self.direction = None
        self.tmp_dir = None
        self.mid_move = False
        self.set_player()
        self.cord = self.translator[self.cell]
        self.old_cord = self.cord
        self.object.x = self.cord[0]
        self.object.y = self.cord[1]
        self.update_animation(moving=False)

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
                self.lvl_score += self.cost_per_gum
                self.score_obj.text = f"score = {self.score+self.lvl_score}"
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

    def on_key_press(self, symbol, modifiers, parent):
        if symbol == key.W or symbol == key.UP:
            self.set_direction("up")
        if symbol == key.D or symbol == key.RIGHT:
            self.set_direction("right")
        if symbol == key.S or symbol == key.DOWN:
            self.set_direction("down")
        if symbol == key.A or symbol == key.LEFT:
            self.set_direction("left")
        ## press p to pause the game
        if symbol == key.P or symbol == key.ESCAPE:
            parent.state = GameState.PAUSE