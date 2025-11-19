from sudoku_explainer.utils import (
    parse_puzzle,
    solve_sudoku_backtracking,
    board_to_string,
)
import time

puzzle = (
    "000000010400000000020000000000050407008000300001090000300400200050100000000806000"
)
print(f"Solving puzzle: {puzzle}")

start = time.time()
board = parse_puzzle(puzzle)
solved = solve_sudoku_backtracking(board)
end = time.time()

print(f"Solved: {solved}")
print(f"Time: {end - start:.4f}s")
print(f"Result: {board_to_string(board)}")
