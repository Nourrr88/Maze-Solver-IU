"""
A very simple Smart Maze Solver using BFS
"""

import tkinter as tk
from tkinter import messagebox
from collections import deque


# The maze has 20 rows and 20 columns.
ROWS = 20
COLS = 20
CELL_SIZE = 25


# Colors make the different cell types easy to see.
EMPTY_COLOR = "white"
WALL_COLOR = "black"
START_COLOR = "#45b649"       # green
GOAL_COLOR = "#e74c3c"        # red
EXPLORED_COLOR = "#9ed8ff"     # light blue
PATH_COLOR = "#ffd84d"        # yellow
GRID_COLOR = "#bdbdbd"


def bfs(rows, cols, walls, start, goal):
    """Find the shortest path from start to goal using Breadth-First Search.

    A cell is written as (row, column), for example (3, 5).

    Returns:
        explored: cells visited by BFS, in visit order
        path: shortest path from start to goal, including start and goal
               (an empty list means that no path was found)
    """

    # The queue stores cells that we still need to visit.
    queue = deque([start])

    # parent remembers how we reached each cell.
    # It also tells us that a cell was already visited.
    parent = {start: None}

    # This list is used to color visited cells on the screen.
    explored = []

    while queue:
        current = queue.popleft()
        explored.append(current)

        # We stop when we reach the goal.
        if current == goal:
            break

        row, col = current

        # The only allowed moves are up, down, left, and right.
        moves = [
            (row - 1, col),  # up
            (row + 1, col),  # down
            (row, col - 1),  # left
            (row, col + 1),  # right
        ]

        for next_cell in moves:
            next_row, next_col = next_cell

            # Ignore cells outside the grid.
            if next_row < 0 or next_row >= rows:
                continue
            if next_col < 0 or next_col >= cols:
                continue

            # Ignore walls and cells that BFS already visited.
            if next_cell in walls or next_cell in parent:
                continue

            parent[next_cell] = current
            queue.append(next_cell)

    # If the goal is not in parent, BFS could not reach it.
    if goal not in parent:
        return explored, []

    # Build the path by walking backward from goal to start.
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent[current]

    # We built it backward, so reverse it.
    path.reverse()
    return explored, path


class MazeApp:
    """The small Tkinter window for drawing and solving the maze."""

    def __init__(self, window):
        self.window = window
        self.window.title("Smart Maze Solver - BFS")

        # These variables store the maze data.
        self.walls = set()
        self.start = None
        self.goal = None
        self.mode = "wall"

        # If the user edits the maze, old solution colors should disappear.
        self.explored = set()
        self.path = set()

        self.make_controls()

        self.canvas = tk.Canvas(
            window,
            width=COLS * CELL_SIZE,
            height=ROWS * CELL_SIZE,
            bg=EMPTY_COLOR,
        )
        self.canvas.pack(padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.click_cell)

        self.status = tk.Label(
            window,
            text="Choose Wall, Start, or Goal, then click a cell.",
            anchor="w",
        )
        self.status.pack(fill="x", padx=10, pady=(0, 10))

        self.draw_grid()

    def make_controls(self):
        """Create the buttons at the top of the window."""
        controls = tk.Frame(self.window)
        controls.pack(pady=(10, 0))

        tk.Button(
            controls,
            text="Wall",
            width=10,
            command=lambda: self.set_mode("wall"),
        ).grid(row=0, column=0, padx=3)

        tk.Button(
            controls,
            text="Start",
            width=10,
            command=lambda: self.set_mode("start"),
        ).grid(row=0, column=1, padx=3)

        tk.Button(
            controls,
            text="Goal",
            width=10,
            command=lambda: self.set_mode("goal"),
        ).grid(row=0, column=2, padx=3)

        tk.Button(
            controls,
            text="Solve with BFS",
            width=15,
            command=self.solve,
        ).grid(row=0, column=3, padx=3)

        tk.Button(
            controls,
            text="Clear Solution",
            width=15,
            command=self.clear_solution,
        ).grid(row=0, column=4, padx=3)

        tk.Button(
            controls,
            text="Reset All",
            width=10,
            command=self.reset_all,
        ).grid(row=0, column=5, padx=3)

    def set_mode(self, mode):
        """Remember what the next mouse click should do."""
        self.mode = mode
        self.status.config(text=f"Mode: {mode}. Click a cell.")

    def cell_from_mouse(self, event):
        """Convert a mouse position into a (row, column) cell."""
        row = event.y // CELL_SIZE
        col = event.x // CELL_SIZE

        if row < 0 or row >= ROWS or col < 0 or col >= COLS:
            return None

        return row, col

    def click_cell(self, event):
        """Change a cell according to the selected mode."""
        cell = self.cell_from_mouse(event)
        if cell is None:
            return

        self.clear_solution()

        if self.mode == "wall":
            # A second click on a wall removes it.
            if cell in self.walls:
                self.walls.remove(cell)
            elif cell != self.start and cell != self.goal:
                self.walls.add(cell)

        elif self.mode == "start":
            # Move the start point to this cell.
            if cell != self.goal and cell not in self.walls:
                self.start = cell

        elif self.mode == "goal":
            # Move the goal point to this cell.
            if cell != self.start and cell not in self.walls:
                self.goal = cell

        self.draw_grid()

    def color_for_cell(self, cell):
        """Choose the color that should be used for one cell."""
        if cell in self.walls:
            return WALL_COLOR
        if cell == self.start:
            return START_COLOR
        if cell == self.goal:
            return GOAL_COLOR
        if cell in self.path:
            return PATH_COLOR
        if cell in self.explored:
            return EXPLORED_COLOR
        return EMPTY_COLOR

    def draw_grid(self):
        """Draw every square in the maze."""
        self.canvas.delete("all")

        for row in range(ROWS):
            for col in range(COLS):
                cell = (row, col)
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.color_for_cell(cell),
                    outline=GRID_COLOR,
                )

    def solve(self):
        """Run BFS and display the answer."""
        if self.start is None or self.goal is None:
            messagebox.showwarning(
                "Missing points",
                "Please choose one Start cell and one Goal cell first.",
            )
            return

        self.explored, path = bfs(
            ROWS,
            COLS,
            self.walls,
            self.start,
            self.goal,
        )
        self.explored = set(self.explored)
        self.path = set(path)
        self.draw_grid()

        if not path:
            self.status.config(
                text=f"No path found. Explored cells: {len(self.explored)}"
            )
            return

        # A path contains both start and goal, so moves = cells - 1.
        moves = len(path) - 1
        self.status.config(
            text=(
                f"Path found! Moves: {moves} | "
                f"Path cost: {moves} | "
                f"Explored cells: {len(self.explored)}"
            )
        )

    def clear_solution(self):
        """Remove only the blue/yellow solution colors."""
        self.explored = set()
        self.path = set()
        if hasattr(self, "canvas"):
            self.draw_grid()
        if hasattr(self, "status"):
            self.status.config(text=f"Mode: {self.mode}. Click a cell.")

    def reset_all(self):
        """Remove walls, start, goal, and the old solution."""
        self.walls = set()
        self.start = None
        self.goal = None
        self.clear_solution()
        self.status.config(text="Everything is clear. Choose a mode and click.")


if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()
