from typing import List, Dict, Any, Generator
from .board import Board
from .strategies.base import Strategy
from .strategies.basics import NakedSingle, HiddenSingle
from .strategies.pairs import NakedPair

class SudokuSolver:
    def __init__(self, board: Board):
        self.board = board
        self.strategies: List[Strategy] = [
            NakedSingle(),
            HiddenSingle(),
            NakedPair(),
            # Add more strategies here as they are implemented
        ]
        self.steps: List[Dict[str, Any]] = []

    def solve(self) -> Generator[Dict[str, Any], None, bool]:
        """
        Yields each step taken to solve the puzzle.
        Returns True if solved, False if stuck.
        """
        while not self.board.is_solved():
            step = self.solve_step()
            if step:
                self.steps.append(step)
                yield step
            else:
                return False
        return True

    def solve_step(self) -> Dict[str, Any]:
        """Attempts to apply one strategy."""
        for strategy in self.strategies:
            result = strategy.apply(self.board)
            if result:
                return result
        return None
