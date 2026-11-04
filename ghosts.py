from collections import deque
from typing import Dict, List, Tuple
import pyglet


class Ghost:
    """ghost entity ooo scary"""

    def __init__(
        self,
        cell: Tuple[int, int],
        coordinator: Dict[Tuple[int, int], Tuple[int, int]],
        maze: List[List[int]],
        size: int,
        batch: pyglet.graphics.Batch,
        color: Tuple[int, int, int, int] = (255, 0, 0, 255),
    ) -> None:
        self.cell = cell
        self.maze = maze
        self.trans = coordinator
        self.translator = coordinator
        self.size = size

        # if starting cell is a solid wall, pick open wall
        if self.maze[self.cell[0]][self.cell[1]] == 15:
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = self.cell[0] + dr, self.cell[1] + dc
                if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] != 15:
                    self.cell = (nr, nc)
                    break

        self.cord = self.trans[self.cell]

        # pglet shape for the ghost will replace with a sprite once i finish them too
        self.object = pyglet.shapes.Rectangle(
            self.cord[0],
            self.cord[1],
            size // 2,
            size // 2,
            color=color,
            batch=batch,
        )

    def set_cord(self) -> None:
        # update screen coordinates and move the shape
        self.cord = self.trans[self.cell]
        self.object.x = self.cord[0]
        self.object.y = self.cord[1]

    def bfs(self, start: Tuple[int, int], target: Tuple[int, int]) -> Tuple[int, int]:
        # already on top of the player just a safeguard
        if start == target:
            return start

        queue = deque([start])
        visited = {start}
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        rows = len(self.maze)
        cols = len(self.maze[0])

        # bitmasks for maze corridors:
        # 1: up, 2: right, 4: down, 8: left
        moves = [
            (1, 0, 1),   # up
            (0, 1, 2),   # right
            (-1, 0, 4),  # down
            (0, -1, 8),  # left
        ]

        found = False
        while queue:
            curr = queue.popleft()
            if curr == target:
                found = True
                break

            r, c = curr
            box = self.maze[r][c]

            for dr, dc, mask in moves:
                # check if theres an open path
                if box & mask == 0:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        nxt = (nr, nc)
                        if nxt not in visited and self.maze[nr][nc] != 15:
                            visited.add(nxt)
                            parent[nxt] = curr
                            queue.append(nxt)

        # cant reach player so stay in place
        if not found:
            return start

        # backtrack from player to start to find first step
        curr = target
        while curr in parent and parent[curr] != start:
            curr = parent[curr]

        return curr

    def move_ghost(self, player_cell: Tuple[int, int]) -> None:
        # find next step with bfs and move
        self.cell = self.bfs(self.cell, player_cell)
        self.set_cord()


ghost = Ghost

# i will add different algos for them so each does a diff job tonight