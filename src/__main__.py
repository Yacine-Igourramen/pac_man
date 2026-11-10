import os
import sys
from ghosts import Ghost
from mazegenerator import MazeGenerator
from pathlib import Path
import pyglet
from pyglet import shapes
from pyglet.math import Mat4
from pyglet.window import key
from parser import parser, Config
import json
import time
from screens import menu_screen, Pause_screen, Win_screen, lose_screen, GameState, leaderboard_screen
from maze import maze_assets

# i put ★★★ in front of my comments so theyre easier for u to find and read 👍🏿
## this is the window class
class GameWindow(pyglet.window.Window):
    def __init__(self, info, conf, leaderboard):
        super().__init__(fullscreen=True, vsync=False)
        self.state = GameState.MENU
        self.info = info
        self.lvl = 0
        self.score_file = conf.highscore_filename
        self.time_limit = conf.level_max_time
        self.pac_gum_cost = conf.points_per_pacgum
        self.ghost_cost = conf.points_per_ghost
        self.super_pac_gum_cost = conf.points_per_super_pacgum
        self.number_of_gum = conf.pacgum
        self.health = conf.lives
        self.game_play = None ## this is the maze class
        self.menu = menu_screen(info[0][2], info[0][3]) ## this is the menu as the name say
        self.pause = Pause_screen(info[0][2], info[0][3])
        self.win = Win_screen(info[0][2], info[0][3])
        self.lose = lose_screen(info[0][2], info[0][3])
        self.leaderboard = leaderboard_screen(info[0][2], info[0][3], leaderboard)
        self.player = None ## the player exists seperately from the maze
        self.ghost_timer = 0.0 ## ★★★ added this pretty self explanatory
        self.lvls_count = len(conf.levels)
        pyglet.clock.schedule_interval(self.update, 1/(info[0][1]*2.5)) ## the refresh rate 

    ## the function that writes to the window with its 3 options
    def on_draw(self):
        self.clear()
        if self.state == GameState.MENU:
            self.menu.menu_batch.draw()
        elif self.state == GameState.PLAYING:
            self.game_play.main_batch.draw()
            self.player.batch.draw()
        elif self.state == GameState.PAUSE:
            self.game_play.main_batch.draw()
            self.player.batch.draw()
            self.pause.pause_batch.draw()
        elif self.state == GameState.WIN:
            self.win.win_batch.draw()
        elif self.state == GameState.GAME_OVER:
            self.lose.lose_batch.draw()
        elif self.state == GameState.LEADER_BOARD:
            self.leaderboard.draw()
    def on_text(self, text):
        if self.state == GameState.WIN:
            self.win.on_text(text)
        if self.state == GameState.GAME_OVER:
            self.lose.on_text(text)

    ## this one handeles key presses
    def on_key_press(self, symbol, modifiers):
        if self.state == GameState.PLAYING:
            self.player.on_key_press(symbol, modifiers, self)
        elif self.state == GameState.PAUSE:
            self.pause.on_key_press(symbol, modifiers, self)
        elif self.state == GameState.MENU:
            self.menu.on_key_press(symbol, modifiers, self)
        elif self.state == GameState.WIN :
            self.win.on_key_press(symbol, modifiers, self, self.leaderboard)
        elif self.state == GameState.GAME_OVER :
            self.lose.on_key_press(symbol, modifiers, self, self.leaderboard)
    
    def on_mouse_motion(self, x, y, dx, dy):
        if self.state == GameState.MENU:
            self.menu.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.state == GameState.MENU:
            self.menu.on_mouse_press(x, y, button, modifiers)

    ## this is the one that get's called many times a second
    def update(self, dt):
        if self.state == GameState.PLAYING:
            ## we move the player which gives us continues movement
            self.player.move_player()

            if self.game_play and self.player:
                ## ★★★ move all 4 ghosts smoothly every frame like player
                for g in self.game_play.ghosts:
                    g.move_ghost(self.player.cell)

                ## ★★★ check if any ghost touches the player
                ## i think the game is too fast paced. needs to be slower
                for g in self.game_play.ghosts:
                    if g.cell == self.player.cell or (
                        abs(g.object.x - self.player.object.x) < self.game_play.size * 0.5
                        and abs(g.object.y - self.player.object.y) < self.game_play.size * 0.5
                    ):
                        ## ★★★ decrement lives counter on top right
                        self.player.health -= 1
                        self.player.lives_obj.text = f'lives = {self.player.health}'
                        ## ★★★ reset player and all ghosts back to starting positions
                        self.player.reset_position()
                        for ghost in self.game_play.ghosts:
                            ghost.reset_position()
                        break
            if self.player.health == 0:
                self.lose.update_score(self.player.score + self.player.lvl_score)
                self.state = GameState.GAME_OVER
                return
            ## below i check if all the pac-gums are eaten then i move to the next lvl
            if all(value is None for value in self.player.pac_gums.values()):
                self.lvl += 1
                if self.lvl == self.lvls_count:
                    self.win.update_score(self.player.score + self.player.lvl_score)
                    self.state = GameState.WIN
                    return
                if self.lvl < len(self.info):
                    self.game_play = maze_assets(self.info[self.lvl][0], self.info[self.lvl][1], self.info[self.lvl][2], self.info[self.lvl][3], self.number_of_gum)
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
    file_path = Path(__file__).parent.parent / conf.highscore_filename
    if file_path.exists() and file_path.stat().st_size > 0:
        with open(file_path, "r") as file:
            data = json.load(file)
    else:  ## this part still needs a check if the file is a valid .json
        data = []
    info = []
    ## we fill info with the data each maze needs
    for i in mazes:
        info.append(size_detector(i.maze))
    ## we make the window
    win = GameWindow(info, conf, data)

    pyglet.app.run()


if __name__ == "__main__":
    main()
