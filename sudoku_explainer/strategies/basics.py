from typing import Optional, Dict, Any
from ..board import Board
from .base import Strategy


class NakedSingle(Strategy):
    def apply(self, board: Board) -> Optional[Dict[str, Any]]:
        for r in range(9):
            for c in range(9):
                if board.get_value(r, c) == 0:
                    candidates = board.get_candidates(r, c)
                    if len(candidates) == 1:
                        val = list(candidates)[0]
                        board.set_value(r, c, val)
                        return {
                            "type": "Naked Single",
                            "row": r,
                            "col": c,
                            "value": val,
                            "explanation": f"Cell ({r + 1}, {c + 1}) has only one possible candidate: {val}",
                        }
        return None


class HiddenSingle(Strategy):
    def apply(self, board: Board) -> Optional[Dict[str, Any]]:
        # Check rows
        for r in range(9):
            counts = {}
            for c in range(9):
                if board.get_value(r, c) == 0:
                    for val in board.get_candidates(r, c):
                        if val not in counts:
                            counts[val] = []
                        counts[val].append(c)

            for val, cols in counts.items():
                if len(cols) == 1:
                    c = cols[0]
                    board.set_value(r, c, val)
                    return {
                        "type": "Hidden Single (Row)",
                        "row": r,
                        "col": c,
                        "value": val,
                        "explanation": f"In row {r + 1}, the value {val} can only go in cell ({r + 1}, {c + 1})",
                    }

        # Check cols
        for c in range(9):
            counts = {}
            for r in range(9):
                if board.get_value(r, c) == 0:
                    for val in board.get_candidates(r, c):
                        if val not in counts:
                            counts[val] = []
                        counts[val].append(r)

            for val, rows in counts.items():
                if len(rows) == 1:
                    r = rows[0]
                    board.set_value(r, c, val)
                    return {
                        "type": "Hidden Single (Column)",
                        "row": r,
                        "col": c,
                        "value": val,
                        "explanation": f"In column {c + 1}, the value {val} can only go in cell ({r + 1}, {c + 1})",
                    }

        # Check boxes
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                counts = {}
                for r in range(br, br + 3):
                    for c in range(bc, bc + 3):
                        if board.get_value(r, c) == 0:
                            for val in board.get_candidates(r, c):
                                if val not in counts:
                                    counts[val] = []
                                counts[val].append((r, c))

                for val, cells in counts.items():
                    if len(cells) == 1:
                        r, c = cells[0]
                        board.set_value(r, c, val)
                        return {
                            "type": "Hidden Single (Box)",
                            "row": r,
                            "col": c,
                            "value": val,
                            "explanation": f"In the box starting at ({br + 1}, {bc + 1}), the value {val} can only go in cell ({r + 1}, {c + 1})",
                        }
        return None
