import pyglet

## the menu screen and its 2 texts
class menu_screen():
    def __init__(self, screen_w, screen_h):
        self.menu_batch = pyglet.graphics.Batch()
        self.txt = []
        self.txt.append(pyglet.text.Label(text="PAC-MAN", font_size=100, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))
        self.txt.append(pyglet.text.Label(text="press ENTER to start", font_size=20, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2-300, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))
        self.txt.append(pyglet.text.Label(text="press ESCAPE to exit", font_size=20, color=(255, 255, 255, 255), x=screen_w//4, y=screen_h//2-350, anchor_x='left', anchor_y='baseline', align='left', multiline=False, batch=self.menu_batch, group=None))


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