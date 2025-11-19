from typing import List
from .board import Board


def parse_puzzle(puzzle_str: str) -> Board:
    """Parses an 81-character string into a Board object."""
    if len(puzzle_str) != 81:
        raise ValueError("Puzzle string must be exactly 81 characters long.")

    grid = []
    for i in range(0, 81, 9):
        row_str = puzzle_str[i : i + 9]
        row = [int(c) if c.isdigit() else 0 for c in row_str]
        grid.append(row)

    return Board(grid)


def format_board_simple(board: Board) -> str:
    """Returns a simple string representation of the board."""
    return str(board)


def board_to_string(board: Board) -> str:
    """Converts a Board object back to an 81-character string."""
    chars = []
    for r in range(9):
        for c in range(9):
            val = board.get_value(r, c)
            chars.append(str(val))
    return "".join(chars)


def solve_sudoku_backtracking(board: Board) -> bool:
    """
    Solves the board using backtracking with MRV heuristic.
    Modifies the board in-place. Returns True if solvable.
    """
    empty = find_empty_mrv(board)
    if not empty:
        return True
    row, col = empty

    for num in range(1, 10):
        if is_valid(board, row, col, num):
            board.grid[row][col] = num
            if solve_sudoku_backtracking(board):
                return True
            board.grid[row][col] = 0

    return False


def find_empty_mrv(board: Board):
    """Finds the empty cell with the fewest valid options (MRV)."""
    min_opts = 10
    best_cell = None

    for r in range(9):
        for c in range(9):
            if board.grid[r][c] == 0:
                opts = 0
                for n in range(1, 10):
                    if is_valid(board, r, c, n):
                        opts += 1

                if opts == 0:
                    return (r, c)  # Dead end, force backtrack

                if opts < min_opts:
                    min_opts = opts
                    best_cell = (r, c)
                    if min_opts == 1:
                        return best_cell

    return best_cell


def is_valid(board: Board, row: int, col: int, num: int) -> bool:
    # Check row
    for c in range(9):
        if board.grid[row][c] == num:
            return False

    # Check col
    for r in range(9):
        if board.grid[r][col] == num:
            return False

    # Check box
    box_r, box_c = (row // 3) * 3, (col // 3) * 3
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            if board.grid[r][c] == num:
                return False

    return True
