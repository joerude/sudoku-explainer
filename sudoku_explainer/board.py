from typing import List, Set, Optional, Tuple

class Board:
    def __init__(self, grid: Optional[List[List[int]]] = None):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.candidates = [[set(range(1, 10)) for _ in range(9)] for _ in range(9)]
        
        if grid:
            for r in range(9):
                for c in range(9):
                    if grid[r][c] != 0:
                        self.set_value(r, c, grid[r][c])

    def set_value(self, row: int, col: int, value: int) -> None:
        """Sets a value in the grid and clears candidates for that cell."""
        self.grid[row][col] = value
        self.candidates[row][col] = set()
        self.update_peers(row, col, value)

    def update_peers(self, row: int, col: int, value: int) -> None:
        """Removes the set value from candidates of all peers."""
        # Row
        for c in range(9):
            if value in self.candidates[row][c]:
                self.candidates[row][c].remove(value)
        
        # Column
        for r in range(9):
            if value in self.candidates[r][col]:
                self.candidates[r][col].remove(value)
        
        # Box
        start_r, start_c = (row // 3) * 3, (col // 3) * 3
        for r in range(start_r, start_r + 3):
            for c in range(start_c, start_c + 3):
                if value in self.candidates[r][c]:
                    self.candidates[r][c].remove(value)

    def get_value(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def get_candidates(self, row: int, col: int) -> Set[int]:
        return self.candidates[row][col].copy()

    def remove_candidate(self, row: int, col: int, value: int) -> bool:
        """Removes a candidate from a cell. Returns True if changed."""
        if value in self.candidates[row][col]:
            self.candidates[row][col].remove(value)
            return True
        return False

    def is_solved(self) -> bool:
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] == 0:
                    return False
        return self.is_valid()

    def is_valid(self) -> bool:
        # Check rows
        for r in range(9):
            seen = set()
            for c in range(9):
                val = self.grid[r][c]
                if val != 0:
                    if val in seen: return False
                    seen.add(val)
        
        # Check cols
        for c in range(9):
            seen = set()
            for r in range(9):
                val = self.grid[r][c]
                if val != 0:
                    if val in seen: return False
                    seen.add(val)

        # Check boxes
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                seen = set()
                for r in range(br, br + 3):
                    for c in range(bc, bc + 3):
                        val = self.grid[r][c]
                        if val != 0:
                            if val in seen: return False
                            seen.add(val)
        return True

    def clone(self) -> 'Board':
        """Creates a deep copy of the board."""
        new_board = Board()
        new_board.grid = [row[:] for row in self.grid]
        new_board.candidates = [
            [c.copy() for c in row] for row in self.candidates
        ]
        return new_board

    def __str__(self) -> str:
        res = []
        for r in range(9):
            if r % 3 == 0 and r != 0:
                res.append("-" * 21)
            row_str = []
            for c in range(9):
                if c % 3 == 0 and c != 0:
                    row_str.append("|")
                val = self.grid[r][c]
                row_str.append(str(val) if val != 0 else ".")
            res.append(" ".join(row_str))
        return "\n".join(res)
