from typing import List
from .board import Board

def parse_puzzle(puzzle_str: str) -> Board:
    """Parses an 81-character string into a Board object."""
    if len(puzzle_str) != 81:
        raise ValueError("Puzzle string must be exactly 81 characters long.")
    
    grid = []
    for i in range(0, 81, 9):
        row_str = puzzle_str[i:i+9]
        row = [int(c) if c.isdigit() else 0 for c in row_str]
        grid.append(row)
    
    return Board(grid)

def format_board_simple(board: Board) -> str:
    """Returns a simple string representation of the board."""
    return str(board)

def board_to_string(board: Board) -> str:
    """Converts the board back to an 81-character string."""
    res = []
    for r in range(9):
        for c in range(9):
            res.append(str(board.get_value(r, c)))
    return "".join(res)
