import pyglet
from pyglet.window import key
import json
from maze import maze_assets, GameState
from player_class import player
from pathlib import Path
from pyglet.window import mouse


class button:
    def __init__(self, name, button, label):
        self.name = name
        self.button = button
        self.label = label

    def click(self):
        pass

## the menu screen and its 2 texts
class menu_screen():
    def __init__(self, screen_w, screen_h):
        self.menu_batch = pyglet.graphics.Batch()
        self.selected = None
        start_button = pyglet.shapes.Rectangle(
            x=(screen_w - 300) / 2,
            y=(screen_h - 50) // 1.9,
            width=300,
            height=50,
            color=(50, 100, 200),
            batch=self.menu_batch
        )
        start_label = pyglet.text.Label(
            "PLAY",
            x=start_button.x + start_button.width / 2,
            y=start_button.y + start_button.height / 2,
            font_size= (screen_h + screen_w)//100,
            anchor_x="center",
            anchor_y="center",
            batch=self.menu_batch
        )
        self.start_button = button("start", start_button, start_label)
        ##
        Exit_button = pyglet.shapes.Rectangle(
            x=(screen_w - 300) / 2,
            y=(screen_h - 50) // 2.9,
            width=300,
            height=50,
            color=(50, 100, 200),
            batch=self.menu_batch
        )

        Exit_label = pyglet.text.Label(
            "EXIT",
            x=Exit_button.x + Exit_button.width / 2,
            y=Exit_button.y + Exit_button.height / 2,
            font_size=(screen_h + screen_w) // 100,
            anchor_x="center",
            anchor_y="center",
            batch=self.menu_batch
        )
        self.exit_button = button("exit", Exit_button, Exit_label)
        ##
        leaderboard_button = pyglet.shapes.Rectangle(
            x=(screen_w - 300) / 2,
            y=(screen_h - 50) // 2.3,
            width=300,
            height=50,
            color=(50, 100, 200),
            batch=self.menu_batch
        )
        leaderboard_label = pyglet.text.Label(
            "LEADERBOARD",
            x=leaderboard_button.x + leaderboard_button.width / 2,
            y=leaderboard_button.y + leaderboard_button.height / 2,
            font_size= (screen_h + screen_w)//110,
            anchor_x="center",
            anchor_y="center",
            batch=self.menu_batch
        )
        self.leaderboard_button = button("leaderboard", leaderboard_button, leaderboard_label)
        ##
        self.buttons = [self.exit_button, self.leaderboard_button, self.start_button]
        self.title = pyglet.text.Label(text="PAC-MAN", font_size=100, color=(255, 255, 255, 255), x=screen_w//2, y=screen_h//1.3, anchor_x='center', anchor_y='center', align='center', multiline=False, batch=self.menu_batch, group=None)

    def on_key_press(self, symbol, modifiers, parent):
        if symbol == key.W:
            if self.selected == None:
                self.selected = self.start_button
            else:
                num = self.buttons.index(self.selected) + 1 if self.buttons.index(self.selected) + 1 < len(self.buttons) else 0
                self.selected = self.buttons[num]
            for i in self.buttons:
                i.button.color =  (50, 100, 200)
            self.selected.button.color = (100, 150, 255)
        if symbol == key.S:
            if self.selected == None:
                self.selected = self.start_button
            else:
                num = self.buttons.index(self.selected) - 1 if self.buttons.index(self.selected) - 1 >= 0 else len(self.buttons)-1
                self.selected = self.buttons[num]
            for i in self.buttons:
                i.button.color =  (50, 100, 200)
            self.selected.button.color = (100, 150, 255)
        if symbol == key.ENTER:
            if self.selected.name == "start":
                parent.game_play = maze_assets(parent.info[0][0], parent.info[0][1], parent.info[0][2], parent.info[0][3], parent.number_of_gum)
                parent.player = player(parent.health, maze=parent.game_play, costs=[parent.pac_gum_cost, parent.super_pac_gum_cost, parent.ghost_cost])
                parent.state = GameState.PLAYING
            if self.selected.name == "exit":
                parent.state = parent.close()
            if self.selected.name == "leaderboard":
                parent.state = GameState.LEADER_BOARD
        if symbol == key.ESCAPE:
            parent.state = parent.close()

    def on_mouse_press(self, x, y, button, modifiers):
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        if (self.exit_button.button.x <= x <= self.exit_button.button.x + self.exit_button.button.width and
            self.exit_button.button.y <= y <= self.exit_button.button.y + self.exit_button.button.height):

            self.exit_button.button.color = (100, 150, 255)
            self.selected = None
        else:
            if self.selected == None:
                self.exit_button.button.color = (50, 100, 200)

        if (self.start_button.button.x <= x <= self.start_button.button.x + self.start_button.button.width and
            self.start_button.button.y <= y <= self.start_button.button.y + self.start_button.button.height):

            self.start_button.button.color = (100, 150, 255)
            self.selected = None
        else:
            if self.selected == None:
                self.start_button.button.color = (50, 100, 200)

        if (self.leaderboard_button.button.x <= x <= self.leaderboard_button.button.x + self.leaderboard_button.button.width and
            self.leaderboard_button.button.y <= y <= self.leaderboard_button.button.y + self.leaderboard_button.button.height):

            self.leaderboard_button.button.color = (100, 150, 255)
            self.selected = None
        else:
            if self.selected == None:
                self.leaderboard_button.button.color = (50, 100, 200)


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
            parent.player.lvl_score = 0
            parent.player.change_maze(parent.game_play)
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
    def on_key_press(self, symbol, modifiers, parent, data):
        if symbol == key.BACKSPACE:
            self.player_name = self.player_name[:-1]
            self.name_label.text = self.player_name
        if symbol == key.ENTER:
            if self.player_name != "":
                file_path = Path(__file__).parent.parent / parent.score_file
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
    def on_key_press(self, symbol, modifiers, parent,):
        if symbol == key.BACKSPACE:
            self.player_name = parent.lose.player_name[:-1]
            self.name_label.text = self.player_name
        if symbol == key.ENTER:
            if self.player_name != "":
                file_path = Path(__file__).parent.parent / parent.score_file
                data.append({self.player_name: parent.player.score})
                with open(file_path, "w") as file:
                    json.dump(data, file, indent=4)
            parent.state = GameState.MENU
        if symbol == key.ESCAPE:
            parent.state = GameState.MENU

class leaderboard_screen():
    def __init__(self, screen_w, screen_h, data):
        self.data = sorted(data, key=lambda x: list(x.values())[0], reverse=True)

        print(data)
