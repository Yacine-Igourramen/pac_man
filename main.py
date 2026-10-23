from mazegenerator import MazeGenerator
import pyglet
from pyglet import shapes
from pyglet.math import Mat4
from pyglet.window import key
from enum import Enum, auto


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
        self.cell = (len(maze)//2, len(maze[0])//2)
        if maze[self.cell[0]][self.cell[1]] == 15:
            self.cell = (self.cell[0], self.cell[1]-1)
        self.dots[self.cell].delete()
        self.dots[self.cell] = None
        self.maze[self.cell[0]][self.cell[1]] = self.maze[self.cell[0]][self.cell[1]] ^ 16
        self.translator = coordinator
        self.cord = (0, 0)
        self.score = 0
        self.set_cord()
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
                            batch=batch,
                            group=None
                        )
        self.object = pyglet.shapes.Rectangle(self.cord[0], self.cord[1], size//2, size//2, color=(255, 25, 55, 255), batch=batch, group=None)

    def set_cord(self):
        if self.maze[self.cell[0]][self.cell[1]] & 16 > 0:
            self.score += 10
            self.score_obj.text = f"score = {self.score}"
            self.dots[self.cell].delete()
            self.dots[self.cell] = None
            self.maze[self.cell[0]][self.cell[1]] = self.maze[self.cell[0]][self.cell[1]] ^ 16
        self.cord = self.translator[self.cell]

    def move_player(self, direction):
        print(direction)
        box = self.maze[self.cell[0]][self.cell[1]]
        if direction == "up" and box & 1 == 0:
            self.cell = (self.cell[0] + 1, self.cell[1])
        elif direction == "right" and box & 2 == 0:
            self.cell = (self.cell[0], self.cell[1] + 1)
        elif direction == "down" and box & 4 == 0:
            self.cell = (self.cell[0] - 1, self.cell[1])
        elif direction == "left" and box & 8 == 0:
            self.cell = (self.cell[0], self.cell[1] - 1)
        else:
            return
        self.set_cord()
        self.object.x = self.cord[0]
        self.object.y = self.cord[1]


class maze_assets():
    def __init__(self, maze, size, width, height):
        self.main_batch = pyglet.graphics.Batch()
        self.boxes = {}
        self.dots = {}
        self.walls = []
        w_cells = len(maze[0])
        h_cells = len(maze)
        w_start = (width-(w_cells*size))//2
        h_start = (height-(h_cells*size))//2
        for c, line in enumerate(maze):
            for i, cell in enumerate(line):
                if cell & 1 :
                    self.walls.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start+size, i*size+w_start+size, c*size+h_start+size, color=(255, 255, 255, 255), batch=self.main_batch, group=None))
                if cell & 2 :
                    self.walls.append(pyglet.shapes.Line(i*size+w_start+size, c*size+h_start+size, i*size+w_start+size, c*size+h_start, color=(255, 255, 255, 255), batch=self.main_batch, group=None))
                if cell & 4 :
                    self.walls.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start, i*size+w_start+size, c*size+h_start, color=(255, 255, 255, 255), batch=self.main_batch, group=None))
                if cell & 8 :
                    self.walls.append(pyglet.shapes.Line(i*size+w_start, c*size+h_start, i*size+w_start, c*size+h_start+size, color=(255, 255, 255, 255), batch=self.main_batch, group=None))
                if cell & 16:
                    self.dots[(c, i)] = pyglet.shapes.Circle((w_start+i*size)+size//2, (h_start+c*size)+size//2, size//14, color=(25, 255, 25, 255), batch=self.main_batch, group=None)
                self.boxes[(c,i)] = ((w_start+i*size)+size//4, (h_start+c*size)+size//4)
        self.player = player(3, self.boxes, maze, size, self.main_batch, self.dots)
        self.walls.append(self.player.object)


class menu_screen():
    def __init__(self, screen_w, screen_h):
        self.menu_batch = pyglet.graphics.Batch()
        self.txt = []
        self.txt.append(pyglet.text.Label(text="PAC-MAN", font_size=100, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))
        self.txt.append(pyglet.text.Label(text="press ENTER to start", font_size=20, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2-300, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))


class GameWindow(pyglet.window.Window):
    def __init__(self, maze, size, width, height):
        super().__init__(fullscreen=True)
        self.state = GameState.MENU
        self.game_play = maze_assets(maze, size, width, height)
        self.direction = None
        self.maze = maze
        self.menu = menu_screen(width, height)
        pyglet.clock.schedule_interval(self.update, 1 / 5)

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
        box = self.maze[self.game_play.player.cell[0]][self.game_play.player.cell[1]]
        if symbol == key.W and box & 1 == 0:
            self.direction = "up"
        if symbol == key.D and box & 2 == 0:
            self.direction = "right"
        if symbol == key.S and box & 4 == 0:
            self.direction = "down"
        if symbol == key.A and box & 8 == 0:
            self.direction = "left"

    def update(self, dt):
        if self.state == GameState.PLAYING:
            self.game_play.player.move_player(self.direction)
        elif self.state == GameState.MENU:
            pass

    


def main():
    ma = MazeGenerator(size=(20, 20))
    ma.generate(15)
    for row_idx, row in enumerate(ma.maze):
        for col_idx, val in enumerate(row):
            if val != 15:
                ma.maze[row_idx][col_idx] = val ^ 16
    ####
    display = pyglet.display.get_display()
    screen = display.get_default_screen()
    screen_width = screen.width
    screen_height = screen.height
    ####
    w_cells = len(ma.maze[0])
    h_cells = len(ma.maze)
    ma.maze.reverse()
    size = (screen_width-200)//w_cells if (screen_width-200)//w_cells < (screen_height-300)//h_cells else (screen_height-300)//h_cells
    print(size)
    win = GameWindow(ma.maze, size, screen.width, screen.height)
    pyglet.app.run()


if __name__ == "__main__":
    main()

