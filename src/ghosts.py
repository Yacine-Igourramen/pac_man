from collections import deque
import heapq
from typing import Dict, List, Tuple
import pyglet

DEFAULT_RESPAWN_COOLDOWN = 5.0 # just getting a feel for this idk if it works good? test and tell me 
DEFAULT_NORMAL_SPEED = 1.0 # normal ghost speed (1.0 = 1 pixel per frame)
DEFAULT_SCARED_SPEED = 0.5 # scared ghost speed (0.5 = 1 pixel every 2 frames) 


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
                group: pyglet.graphics.Group = None,
                algo: str = "bfs",
            ) -> None:
        self.cell = cell
        self.maze = maze
        self.last_cell = None ## this is to prevent 180 backtracking it will keep track of the last cell it was on
        self.translator = coordinator
        self.size = size
        self.algo = algo
        self.base_color = color
        self.respawn_cooldown = DEFAULT_RESPAWN_COOLDOWN
        self.cooldown_timer = 0.0
        self.normal_speed = DEFAULT_NORMAL_SPEED
        self.scared_speed = DEFAULT_SCARED_SPEED
        self.scared = False
        self.move_accumulator = 0.0

        # if starting cell is a solid wall, pick open wall
        if self.maze[self.cell[0]][self.cell[1]] == 15:
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = self.cell[0] + dr, self.cell[1] + dc
                if 0 <= nr < len(maze) and 0 <= nc < len(maze[0]) and maze[nr][nc] != 15:
                    self.cell = (nr, nc)
                    break

        ## remember starting corner to reset when player is touched
        self.start_cell = self.cell
        self.cord = self.translator[self.cell]
        ## tracks previous position and animation state like player
        self.old_cord = self.cord
        self.mid_move = False
        self.offset = (size - size // 2) // 2 # for centering them

        # pglet shape for the ghost will replace with a sprite once i finish them too
        self.object = pyglet.shapes.Rectangle(
            self.cord[0] + self.offset,
            self.cord[1] + self.offset,
            size // 2,
            size // 2,
            color=color,
            batch=batch,
            group=group,
        )

    def set_cord(self) -> None:
        ## save old screen position before updating to new one
        self.old_cord = self.cord
        self.cord = self.translator[self.cell]

    ## moves the ghost smoothly on screen by distance pixels like player
    def move(self) -> None:
        speed = self.scared_speed if self.scared else self.normal_speed
        self.move_accumulator += speed
        if self.move_accumulator < 1.0:
            return
        step = int(self.move_accumulator)
        self.move_accumulator -= step

        x = self.old_cord[0]
        y = self.old_cord[1]

        if self.cord[0] > x:
            x = min(x + step, self.cord[0])
        elif self.cord[0] < x:
            x = max(x - step, self.cord[0])

        if self.cord[1] > y:
            y = min(y + step, self.cord[1])
        elif self.cord[1] < y:
            y = max(y - step, self.cord[1])

        self.old_cord = (x, y)
        self.object.x = x + self.offset
        self.object.y = y + self.offset

        if self.old_cord == self.cord:
            self.mid_move = False

    ## ★★★ resets ghost back to its starting corner
    def reset_position(self) -> None:
        self.cell = self.start_cell
        self.last_cell = None
        self.mid_move = False
        self.scared = False
        self.cooldown_timer = 0.0
        self.move_accumulator = 0.0
        self.cord = self.translator[self.cell]
        self.old_cord = self.cord
        self.object.x = self.cord[0] + self.offset
        self.object.y = self.cord[1] + self.offset
        self.object.color = self.base_color

    def bfs(self, start: Tuple[int, int], target: Tuple[int, int]) -> Tuple[int, int]:
        """obvious"""

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

        # count open paths from start tile to detect dead ends
        start_box = self.maze[start[0]][start[1]]
        open_ways = 0
        for dr, dc, mask in moves:
            if start_box & mask == 0:
                nr, nc = start[0] + dr, start[1] + dc
                if 0 <= nr < rows and 0 <= nc < cols and self.maze[nr][nc] != 15:
                    open_ways += 1
        is_dead_end = (open_ways <= 1)

        found = False
        while queue:
            curr = queue.popleft()
            if curr == target:
                found = True

                break
            # row anc collumn pair
            r, c = curr
            box = self.maze[r][c]

            for dr, dc, mask in moves:
                # check if theres an open path
                if box & mask == 0:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        nxt = (nr, nc)
                        if nxt not in visited and self.maze[nr][nc] != 15:
                            ## allow backtracking only if trapped in a dead end (mainly happens inside the 42 pattern)
                            if curr != start or is_dead_end or nxt != self.last_cell:
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

    def reverse_bfs(self, start: Tuple[int, int], player_cell: Tuple[int, int]) -> Tuple[int, int]:
        queue = deque([player_cell])
        dist = {player_cell: 0}

        rows = len(self.maze)
        cols = len(self.maze[0])

        moves = [
            (1, 0, 1),
            (0, 1, 2),
            (-1, 0, 4),
            (0, -1, 8),
        ]

        while queue:
            curr = queue.popleft()
            r, c = curr
            box = self.maze[r][c]
            for dr, dc, mask in moves:
                if box & mask == 0:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and self.maze[nr][nc] != 15:
                        nxt = (nr, nc)
                        if nxt not in dist:
                            dist[nxt] = dist[curr] + 1
                            queue.append(nxt)

        start_box = self.maze[start[0]][start[1]]
        open_ways = 0
        valid_moves = []
        for dr, dc, mask in moves:
            if start_box & mask == 0:
                nr, nc = start[0] + dr, start[1] + dc
                if 0 <= nr < rows and 0 <= nc < cols and self.maze[nr][nc] != 15:
                    open_ways += 1
                    valid_moves.append((nr, nc))

        is_dead_end = (open_ways <= 1)
        filtered = [m for m in valid_moves if is_dead_end or m != self.last_cell]
        candidates = filtered if filtered else valid_moves

        if not candidates:
            return start

        best_cell = candidates[0]
        max_dist = -1
        for cell in candidates:
            d = dist.get(cell, -1)
            if d > max_dist:
                max_dist = d
                best_cell = cell

        return best_cell

    def greedy_search(self, start: Tuple[int, int], target: Tuple[int, int]) -> Tuple[int, int]:
        if start == target:
            return start

        count = 0
        h_start = abs(start[0] - target[0]) + abs(start[1] - target[1])
        pq = [(h_start, count, start)]
        visited = {start}
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {}

        rows = len(self.maze)
        cols = len(self.maze[0])
        moves = [
            (1, 0, 1),
            (0, 1, 2),
            (-1, 0, 4),
            (0, -1, 8),
        ]

        found = False
        start_box = self.maze[start[0]][start[1]]
        open_ways = 0
        for dr, dc, mask in moves:
            if start_box & mask == 0:
                nr, nc = start[0] + dr, start[1] + dc
                if 0 <= nr < rows and 0 <= nc < cols and self.maze[nr][nc] != 15:
                    open_ways += 1
        is_dead_end = (open_ways <= 1)

        while pq:
            _, _, curr = heapq.heappop(pq)
            if curr == target:
                found = True
                break

            r, c = curr
            box = self.maze[r][c]
            for dr, dc, mask in moves:
                if box & mask == 0:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and self.maze[nr][nc] != 15:
                        nxt = (nr, nc)
                        if nxt not in visited:
                            if curr != start or is_dead_end or nxt != self.last_cell:
                                visited.add(nxt)
                                parent[nxt] = curr
                                count += 1
                                h = abs(nr - target[0]) + abs(nc - target[1])
                                heapq.heappush(pq, (h, count, nxt))

        if not found or target not in parent:
            return start

        curr = target
        while curr in parent and parent[curr] != start:
            curr = parent[curr]

        return curr

    def move_ghost(
        self,
        player_cell: Tuple[int, int],
        red_cell: Tuple[int, int] = None,
        scared: bool = False,
    ) -> None:
        if self.cooldown_timer > 0:
            return

        self.scared = scared
        self.object.color = (50, 50, 255, 255) if scared else self.base_color

        ## if mid move continue moving smoothly towards target
        if self.mid_move:
            self.move()
            return

        if scared:
            nxt_cell = self.reverse_bfs(self.cell, player_cell)
        elif self.algo == "greedy" and red_cell is not None:
            nxt_cell = self.greedy_search(self.cell, red_cell)
        else:
            nxt_cell = self.bfs(self.cell, player_cell)

        if nxt_cell != self.cell:
            self.last_cell = self.cell
            self.cell = nxt_cell
            self.set_cord()
            self.mid_move = True
