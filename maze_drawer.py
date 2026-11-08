import pyglet
import math
import time
from mazegenerator import MazeGenerator

from pyglet import gl

tile_map = {
    # "label" : [off_x, off_y, cell_x, cell_y, rep_x, rep_y]
    "tile": [0, 0, 64, 64, 4, 4],
}

class Sheet:
    
    def __init__(self, file_path: str, map: dict, go_vert=True):
        self.file_path = file_path
        self.map = map
        self.full_image = pyglet.image.load(file_path)
        self.texture = self.full_image.get_texture()
        self.tiles = map.keys()
        self.f_tile = list(map.keys())[0]
        self.govert = go_vert

        gl.glTexParameteri(self.texture.target, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)

        self.sheet = self._split_sheet()
        self.full_sheet = self._get_full_sheet()
        

    def _split_sheet(self):

        res = {}
        if self.govert:
            for t, m in self.map.items():
                rows = []
                for i in range(m[4]):
                    imgs = []
                    for j in range(m[5]):
                        imgs.append(self.texture.get_region(m[0] + m[2]*i, m[1] + m[3]*j, m[2], m[3]))
                    rows.append(imgs)
                res[t] = rows
        else:
            for t, m in self.map.items():
                rows = []
                for i in range(m[5]):
                    imgs = []
                    for j in range(m[4]):
                        imgs.append(self.texture.get_region(m[0] + m[3]*j, m[1] + m[3]*i, m[3], m[2]))
                    rows.append(imgs)
                res[t] = rows
        
        return res

    def _get_full_sheet(self):

        full_sheets = {}

        for s, v in self.sheet.items():
            full_sheet = []
            for i in v:
                full_sheet += i
            
            full_sheets.update({s : full_sheet})

        return full_sheets

class MazeVisualizer():

    def __init__(self, maze, init_scale, sheet, maze_offset):
        self.maze = maze
        self.scale = init_scale
        self.M_HEIGHT = len(maze)
        self.M_WIDTH = len(maze[0])
        self.maze_offset = maze_offset
        self.sheet = sheet
        self.vis_x = self.M_WIDTH * 2 + 1
        self.vis_y = self.M_HEIGHT * 2 + 1
        self.m_x = self.maze_offset[0]
        self.m_y = self.maze_offset[1]

        self.vis_map = self._get_vis_array()
        self.sur_map = self._get_sur_array()
        self.sprites = self._place_sprites()

        for i in self.vis_map:
            print(i)
        
        print("------------")

    
    def update_visuals(self):
        self.sprites = self._place_sprites()
    
    def _get_vis_array(self):

        vis_maze = [[0] * self.vis_x for _ in range(self.vis_y)]
        
        for j, row in enumerate(self.maze):
            for i, v in enumerate(row):

                focus = (i * 2 + 1, j * 2 + 1)

                # NORTH
                vis_maze[focus[1] - 1][focus[0]] |= v & 1
                vis_maze[focus[1] - 1][focus[0] + 1] |= v & 1
                vis_maze[focus[1] - 1][focus[0] - 1] |= v & 1
                # EAST
                vis_maze[focus[1]][focus[0] + 1] |= (v & 2) // 2
                vis_maze[focus[1] + 1][focus[0] + 1] |= (v & 2) // 2
                #vis_maze[focus[1] - 1][focus[0] + 1] |= (v & 2) // 2
                # SOUTH
                vis_maze[focus[1] + 1][focus[0]] |= (v & 4) // 4
                vis_maze[focus[1] + 1][focus[0] + 1] |= (v & 4) // 4
                # WEST
                vis_maze[focus[1]][focus[0] - 1] |= (v & 8) // 8
                vis_maze[focus[1] + 1][focus[0] - 1] |= (v & 8) // 8
        
        return vis_maze

    def _get_sur_array(self):

        sur_map = []

        for j, row in enumerate(self.vis_map):
                lis = []

                for i, v in enumerate(row):
                    sur = 0
                    if v:
                        if i > 0:
                            sur += (self.vis_map[j][i - 1]) * 8
                        if j > 0:
                            sur += (self.vis_map[j - 1][i]) * 1
                        if i < self.vis_x - 1:
                            sur += (self.vis_map[j][i + 1]) * 2
                        if j < self.vis_y - 1:
                            sur += (self.vis_map[j + 1][i]) * 4
                        
                    lis.append(sur)

                sur_map.append(lis)

        sur_map.reverse()
                
        return sur_map

    def _place_sprites(self):

        sprites = []

        for j, row in enumerate(self.sur_map):
            for i, v in enumerate(row):
                
                x_pos = self.m_x + (i * 64 * self.scale)
                y_pos = self.m_y + (j * 64 * self.scale)
                
                sprt = pyglet.sprite.Sprite(self.sheet.full_sheet["tile"][v])

                sprt.x = x_pos
                sprt.y = y_pos
                sprt.scale = self.scale

                sprites.append(sprt)
        
        return sprites

window = pyglet.window.Window(1920, 1000)

maze_sheet = Sheet("maze.png", tile_map)

scale = 3

mg = MazeGenerator((3, 3), True)

maze = mg.generate()

mv = MazeVisualizer(mg.maze, scale, maze_sheet, (0,0))

@window.event
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(0.05, 0.05, 0.15, 1)
    for s in mv.sprites:
        s.draw()

pyglet.app.run()