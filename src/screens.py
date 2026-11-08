import pyglet
from pyglet.window import key
import json
from maze import maze_assets, GameState
from player_class import player
from pathlib import Path


## the menu screen and its 2 texts
class menu_screen():
    def __init__(self, screen_w, screen_h):
        self.menu_batch = pyglet.graphics.Batch()
        self.txt = []
        self.txt.append(pyglet.text.Label(text="PAC-MAN", font_size=100, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))
        self.txt.append(pyglet.text.Label(text="press ENTER to start", font_size=20, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2-300, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))
        self.txt.append(pyglet.text.Label(text="press ESCAPE to exit", font_size=20, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2-350, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))
    def on_key_press(self, symbol, modifiers, parent):
        if symbol == key.ENTER:
            parent.game_play = maze_assets(parent.info[0][0], parent.info[0][1], parent.info[0][2], parent.info[0][3], parent.number_of_gum)
            parent.player = player(parent.health, maze=parent.game_play, costs=[parent.pac_gum_cost, parent.super_pac_gum_cost, parent.ghost_cost])
            parent.state = GameState.PLAYING
        if symbol == key.ESCAPE:
            parent.state = parent.close()


class Pause_screen():
    def __init__(self, screen_w, screen_h):
        self.pause_batch = pyglet.graphics.Batch()
        self.assets = []
        self.assets.append(pyglet.shapes.Rectangle(x=0, y=0, width=screen_w, height=screen_h, color=(0, 0, 0), batch=self.pause_batch))
        self.assets[-1].opacity = 150
        self.assets.append(pyglet.shapes.Rectangle(x=screen_w//4, y=screen_h//4, width=screen_w//2, height=screen_h//2, color=(0, 0, 0), batch=self.pause_batch))
        self.assets.append(pyglet.text.Label(text=f'paused', font_name=None,font_size=50, color=(255, 255, 255, 255),x=screen_w/2-150,y=screen_h//2+50,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.pause_batch))
        self.assets.append(pyglet.text.Label(text=f'press p to continue', font_name=None,font_size=20, color=(255, 255, 255, 255),x=screen_w/2-100,y=screen_h//2,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.pause_batch))
        self.assets.append(pyglet.text.Label(text=f'press R to restart', font_name=None, font_size=20, color=(255, 255, 255, 255),x=screen_w/2-100,y=screen_h//2-50,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.pause_batch))
        self.assets.append(pyglet.text.Label(text=f'press ESCAPE to exit', font_name=None, font_size=20, color=(255, 255, 255, 255),x=screen_w/2-100,y=screen_h//2-100,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.pause_batch))
    def on_key_press(self, symbol, modifiers, parent):
        if symbol == key.P:
            parent.state = GameState.PLAYING
        if symbol == key.R:
            parent.game_play = maze_assets(parent.info[0][0], parent.info[0][1], parent.info[0][2], parent.info[0][3], parent.number_of_gum)
            parent.player = player(parent.health, maze=parent.game_play, costs=[parent.pac_gum_cost, parent.super_pac_gum_cost, parent.ghost_cost])
            parent.state = GameState.PLAYING
        if symbol == key.ESCAPE:
            parent.game_play = None
            parent.state = GameState.MENU


class Win_screen():
    def __init__(self, screen_w, screen_h):
        self.win_batch = pyglet.graphics.Batch()
        self.assets = []
        self.assets.append(pyglet.shapes.Rectangle(x=0, y=0, width=screen_w, height=screen_h, color=(0, 0, 0), batch=self.win_batch))
        self.assets.append(pyglet.text.Label(text=f'you won', font_name=None,font_size=100, color=(255, 255, 255, 255),x=screen_w//2-150,y=screen_h//2+50,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.win_batch))
        self.player_name = ""
        self.assets.append(pyglet.text.Label(text=f'enter your name', font_name=None,font_size=20, color=(255, 255, 255, 255),x=screen_w//2-100,y=screen_h//2,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.win_batch))
        self.name_label = pyglet.text.Label(
                            self.player_name,
                            font_size=70,
                            x=screen_w/2-100, y=screen_h//2-100,
                            anchor_x="center",
                            batch=self.win_batch,
                        )
        self.score = pyglet.text.Label(text=f"score: 0", font_name=None,font_size=30, color=(255, 255, 255, 255),x=screen_w//2-200,y=screen_h//2-150,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.win_batch)

    def update_score(self, score):
        self.score.text = f"score: {score}"
    def on_text(self, text):
        self.player_name += text
        self.name_label.text = self.player_name
    def on_key_press(self, symbol, modifiers, parent):
        if symbol == key.BACKSPACE:
            self.player_name = self.player_name[:-1]
            self.name_label.text = self.player_name
        if symbol == key.ENTER:
            if self.player_name != "":
                file_path = Path(__file__).parent.parent / parent.score_file
                if file_path.exists() and file_path.stat().st_size > 0:
                    with open(file_path, "r") as file:
                        data = json.load(file)
                else:  ## this part still needs a check if the file is a valid .json
                    data = []
                data.append({self.player_name: parent.player.score})
                with open(file_path, "w") as file:
                    json.dump(data, file, indent=4)
            parent.state = GameState.MENU
        if symbol == key.ESCAPE:
            parent.state = GameState.MENU


class lose_screen():
    def __init__(self, screen_w, screen_h):
        self.lose_batch = pyglet.graphics.Batch()
        self.assets = []
        self.assets.append(pyglet.shapes.Rectangle(x=0, y=0, width=screen_w, height=screen_h, color=(0, 0, 0), batch=self.lose_batch))
        self.assets.append(pyglet.text.Label(text=f'you are dead', font_name=None,font_size=100, color=(255, 255, 255, 255),x=screen_w//2-150,y=screen_h//2+50,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.lose_batch))
        self.player_name = ""
        self.assets.append(pyglet.text.Label(text=f'enter your name', font_name=None,font_size=20, color=(255, 255, 255, 255),x=screen_w//2-100,y=screen_h//2,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.lose_batch))
        self.name_label = pyglet.text.Label(
                            self.player_name,
                            font_size=70,
                            x=screen_w/2-100, y=screen_h//2-100,
                            anchor_x="center",
                            batch=self.lose_batch,
                        )
        self.score = pyglet.text.Label(text=f"score: 0", font_name=None,font_size=30, color=(255, 255, 255, 255),x=screen_w//2-200,y=screen_h//2-150,width=None,height=None,anchor_x='left',anchor_y='baseline',align='left',multiline=False,batch=self.lose_batch)

    def update_score(self, score):
        self.score.text = f"score: {score}"
    def on_text(self, text):
        self.player_name += text
        self.name_label.text = self.player_name
    def on_key_press(self, symbol, modifiers, parent):
        if symbol == key.BACKSPACE:
            self.player_name = parent.lose.player_name[:-1]
            self.name_label.text = self.player_name
        if symbol == key.ENTER:
            if self.player_name != "":
                file_path = Path(__file__).parent.parent / parent.score_file
                if file_path.exists() and file_path.stat().st_size > 0:
                    with open(file_path, "r") as file:
                        data = json.load(file)
                else:  ## this part still needs a check if the file is a valid .json
                    data = []
                data.append({self.player_name: parent.player.score})
                with open(file_path, "w") as file:
                    json.dump(data, file, indent=4)
            parent.state = GameState.MENU
        if symbol == key.ESCAPE:
            parent.state = GameState.MENU