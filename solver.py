import random
import copy

# --------------------------
# Generate a full solved grid
# --------------------------

def solve_grid(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                for num in range(1, 10):
                    if valid_move(grid, i, j, num):
                        grid[i][j] = num
                        if solve_grid(grid):
                            return True
                        grid[i][j] = 0
                return False
    return True


def valid_move(grid, r, c, num):
    if num in grid[r]:
        return False
    if num in [grid[x][c] for x in range(9)]:
        return False

    br = (r // 3) * 3
    bc = (c // 3) * 3
    for i in range(3):
        for j in range(3):
            if grid[br+i][bc+j] == num:
                return False
    return True


def generate_full_grid():
    grid = [[0] * 9 for _ in range(9)]
    solve_grid(grid)
    return grid


# --------------------------
# Remove cells for difficulty
# --------------------------

def make_puzzle(grid, difficulty="easy"):
    puzzle = copy.deepcopy(grid)

    if difficulty == "easy":
        holes = 40
    elif difficulty == "medium":
        holes = 50
    else:
        holes = 58

    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)

    for i in range(holes):
        r, c = positions[i]
        puzzle[r][c] = 0

    return puzzle


# --------------------------
# Export puzzle + solution
# --------------------------

def get_sudoku(difficulty="easy"):
    full = generate_full_grid()
    puzzle = make_puzzle(full, difficulty)
    return puzzle, full
