import os
import sys

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


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class player():
    def __init__(self, health, coordinator, maze, size, batch, dots):
        self.name = "pac man"
        self.health = health
        self.maze = maze
        self.dots = dots
        self.direction = None
        self.tmp_dir = None
        self.cell = (len(maze)//2, len(maze[0])//2)
        if maze[self.cell[0]][self.cell[1]] == 15:
            self.cell = (self.cell[0], self.cell[1]-1)
        self.dots[self.cell].delete()
        self.dots[self.cell] = None
        self.maze[self.cell[0]][self.cell[1]] = self.maze[self.cell[0]][self.cell[1]] ^ 16
        self.translator = coordinator
        self.cord = self.translator[self.cell]
        self.old_cord = (0, 0)
        self.score = 0
        self.mid_move = False
        self.score_obj = pyglet.text.Label(
                            text=f'score = {self.score}',
                            font_name=None,
                            font_size=50,
                            italic=False,
                            color=(255, 255, 255, 255),
                            x=10,
                            y=10,
                            width=None,
                            height=None,
                            anchor_x='left',
                            anchor_y='baseline',
                            align='left',
                            multiline=False,
                            batch=batch
                        )
        image_path = os.path.join(os.path.dirname(__file__), "player.png")
        sheet = pyglet.image.load(image_path)
        grid = pyglet.image.ImageGrid(sheet, 4, 4)
        # resting stances:
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
        # to start game in neutral pos
        self.object = pyglet.sprite.Sprite(self.resting_stances["down"], x=self.cord[0], y=self.cord[1], batch=batch)
        self.object.scale = size / self.resting_stances["down"].width

    def update_animation(self, moving=False):
        dir_key = self.direction if self.direction in self.animations else "down"
        target = self.animations[dir_key] if moving else self.resting_stances[dir_key]
        if self.object.image is not target:
            self.object.image = target

    def set_cord(self):
        if self.maze[self.cell[0]][self.cell[1]] & 16 > 0:
            self.score += 10
            self.score_obj.text = f"score = {self.score}"
            self.dots[self.cell].delete()
            self.dots[self.cell] = None
            self.maze[self.cell[0]][self.cell[1]] = self.maze[self.cell[0]][self.cell[1]] ^ 16
        self.old_cord = self.cord
        self.cord = self.translator[self.cell]

    def move(self):
        print(self.old_cord, self.cord)
        if self.old_cord == self.cord:
            self.mid_move = False
            return
        x = self.old_cord[0]
        y = self.old_cord[1]
        move = 1
        if self.cord[0] > self.old_cord[0]:
            x += move
        if self.cord[1] > self.old_cord[1]:
            y += move
        if self.cord[0] < self.old_cord[0]:
            x -= move
        if self.cord[1] < self.old_cord[1]:
            y -= move
        self.old_cord = (x, y)
        self.object.x = self.old_cord[0]
        self.object.y = self.old_cord[1]

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

    def move_player(self):
        if self.mid_move:
            self.move()
            return
        box = self.maze[self.cell[0]][self.cell[1]]
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
        self.set_cord()
        self.mid_move = True
        self.update_animation(moving=True)


class maze_assets():
    def __init__(self, maze, size, width, height):
        self.main_batch = pyglet.graphics.Batch()
        self.boxes = {}
        ##self.floor = []
        self.dots = {}
        self.walls = []
        w_cells = len(maze[0])
        h_cells = len(maze)
        w_start = (width-(w_cells*size))//2
        h_start = (height-(h_cells*size))//2
        for c, line in enumerate(maze):
            for i, cell in enumerate(line):
                if cell & 1 :
                    self.walls.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start+size, i*size+w_start+size, c*size+h_start+size, color=(255, 255, 255, 255), batch=self.main_batch, group=None, thickness=5))
                if cell & 2 :
                    self.walls.append(pyglet.shapes.Line(i*size+w_start+size, c*size+h_start+size, i*size+w_start+size, c*size+h_start, color=(255, 255, 255, 255), batch=self.main_batch, group=None, thickness=5))
                if cell & 4 :
                    self.walls.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start, i*size+w_start+size, c*size+h_start, color=(255, 255, 255, 255), batch=self.main_batch, group=None, thickness=5))
                if cell & 8 :
                    self.walls.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start, i*size+w_start, c*size+h_start+size, color=(255, 255, 255, 255), batch=self.main_batch, group=None, thickness=5))
                if cell & 16:
                    self.dots[(c, i)] = pyglet.shapes.Circle((w_start+i*size)+size//2, (h_start+c*size)+size//2, size//14, color=(25, 255, 25, 255), batch=self.main_batch, group=None)
                self.boxes[(c, i)] = (w_start + i * size, h_start + c * size)
        image_path = os.path.join(os.path.dirname(__file__), "floor.png")
        image = pyglet.image.load(image_path)
        self.player = player(3, self.boxes, maze, size, self.main_batch, self.dots)
        self.walls.append(self.player.object)


class menu_screen():
    def __init__(self, screen_w, screen_h):
        self.menu_batch = pyglet.graphics.Batch()
        self.txt = []
        self.txt.append(pyglet.text.Label(text="PAC-MAN", font_size=100, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))
        self.txt.append(pyglet.text.Label(text="press ENTER to start", font_size=20, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2-300, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))


class GameWindow(pyglet.window.Window):
    def __init__(self, info):
        super().__init__(fullscreen=True)
        self.state = GameState.MENU
        self.info = info
        self.lvl = 0
        self.game_play = maze_assets(info[0][0], info[0][1], info[0][2], info[0][3])
        self.menu = menu_screen(info[0][2], info[0][3])
        pyglet.clock.schedule_interval(self.update, 1/(info[0][1]*5))

    def on_draw(self):
        self.clear()
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_gameplay()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

    def draw_gameplay(self):
        self.game_play.main_batch.draw()

    def draw_menu(self):
        self.menu.menu_batch.draw()

    def on_key_press(self, symbol, modifiers):
        if self.state == GameState.PLAYING:
            if symbol == key.W or symbol == key.UP:
                self.game_play.player.set_direction("up")
            if symbol == key.D or symbol == key.RIGHT:
                self.game_play.player.set_direction("right")
            if symbol == key.S or symbol == key.DOWN:
                self.game_play.player.set_direction("down")
            if symbol == key.A or symbol == key.LEFT:
                self.game_play.player.set_direction("left")
            if symbol == key.SPACE:
                if hasattr(self.game_play, "player") and hasattr(self.game_play.player, "object"):
                    self.game_play.player.object.delete()
                self.lvl += 1
                self.game_play = maze_assets(self.info[self.lvl][0], self.info[self.lvl][1], self.info[self.lvl][2], self.info[self.lvl][3])
                pyglet.clock.unschedule(self.update)
                pyglet.clock.schedule_interval(self.update, 1/(self.info[self.lvl][1]*5))
        if self.state == GameState.MENU:
            if symbol == key.ENTER:
                self.state = GameState.PLAYING
            if symbol == key.ESCAPE:
                self.state = self.close()

    def update(self, dt):
        if self.state == GameState.PLAYING:
            self.game_play.player.move_player()
        elif self.state == GameState.MENU:
            pass


def size_detector(maze):
    display = pyglet.display.get_display()
    screen = display.get_default_screen()
    screen_width = screen.width
    screen_height = screen.height
    ####
    w_cells = len(maze[0])
    h_cells = len(maze)
    maze.reverse()
    size = (screen_width-200)//w_cells if (screen_width-200)//w_cells < (screen_height-300)//h_cells else (screen_height-300)//h_cells
    print(size)
    return [maze, size, screen_width, screen_height]


def main():
    if len(sys.argv) == 1:
        sys.argv.append("config.json")
    conf = parser(sys.argv)
    mazes = []
    for i in conf.levels:
        mazes.append(MazeGenerator(size=(i["width"], i["height"])))
        mazes[-1].generate(conf.seed)
        for row_idx, row in enumerate(mazes[-1].maze):
            for col_idx, val in enumerate(row):
                if val != 15:
                    mazes[-1].maze[row_idx][col_idx] = val ^ 16
    info = []
    for i in mazes:
        info.append(size_detector(i.maze))
    win = GameWindow(info)

    pyglet.app.run()


if __name__ == "__main__":
    main()
