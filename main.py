import argparse
import sys
from sudoku_explainer.board import Board
from sudoku_explainer.utils import parse_puzzle, format_board_simple
from sudoku_explainer.solver import SudokuSolver

def main():
    parser = argparse.ArgumentParser(description="Sudoku Explainer CLI")
    parser.add_argument("--puzzle", type=str, help="81-character puzzle string", required=False)
    args = parser.parse_args()

    puzzle_str = args.puzzle
    if not puzzle_str:
        # Default hard puzzle if none provided
        # This is just a placeholder for now
        print("No puzzle provided. Using a default sample.")
        puzzle_str = "000000010400000000020000000000050407008000300001090000300400200050100000000806000"

    try:
        board = parse_puzzle(puzzle_str)
    except ValueError as e:
        print(f"Error parsing puzzle: {e}")
        sys.exit(1)

    print("Initial Board:")
    print(format_board_simple(board))
    print("\nSolving...\n")

    solver = SudokuSolver(board)
    solved = False
    
    # Iterate through the generator to get steps
    for step in solver.solve():
        print(f"Strategy: {step['type']}")
        print(f"Explanation: {step['explanation']}")
        print("-" * 20)
    
    if board.is_solved():
        print("\nSolved Board:")
        print(format_board_simple(board))
        print("\nPuzzle Solved Successfully!")
    else:
        print("\nStuck! Could not solve further with implemented strategies.")
        print("Current Board State:")
        print(format_board_simple(board))

if __name__ == "__main__":
    main()
