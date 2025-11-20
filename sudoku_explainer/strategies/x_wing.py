from typing import Optional, Dict, Any, List, Tuple
from ..board import Board
from .base import Strategy


class XWing(Strategy):
    """Implements the X-Wing strategy for eliminating candidates.

    For each digit, finds two rows (or columns) where the digit appears
    as a candidate in exactly two columns (or rows), and those columns
    are the same for both rows — forming an X-Wing rectangle. Then the
    digit can be removed from other cells in those two columns (or rows).
    """

    def apply(self, board: Board) -> Optional[Dict[str, Any]]:
        # Check rows as base
        for digit in range(1, 10):
            row_positions = []  # list of (row_index, set(columns_with_candidate))
            for r in range(9):
                cols = set()
                for c in range(9):
                    if board.get_value(r, c) == 0 and digit in board.get_candidates(r, c):
                        cols.add(c)
                if 1 < len(cols) <= 2:
                    row_positions.append((r, cols))

            # look for two rows with identical column sets of size 2
            for i in range(len(row_positions)):
                r1, cols1 = row_positions[i]
                if len(cols1) != 2:
                    continue
                for j in range(i + 1, len(row_positions)):
                    r2, cols2 = row_positions[j]
                    if cols1 == cols2:
                        # Found an X-Wing in rows r1 and r2 across columns in cols1
                        eliminated = []
                        for c in cols1:
                            for r in range(9):
                                if r in (r1, r2):
                                    continue
                                if board.get_value(r, c) == 0 and digit in board.get_candidates(r, c):
                                    board.remove_candidate(r, c, digit)
                                    eliminated.append((r, c, digit))
                        if eliminated:
                            return {
                                "type": "X-Wing (Rows)",
                                "digit": digit,
                                "rows": (r1, r2),
                                "cols": tuple(sorted(list(cols1))),
                                "candidates_removed": eliminated,
                                "explanation": f"Digit {digit} forms an X-Wing on rows {r1 + 1} and {r2 + 1} in columns {', '.join(str(x+1) for x in sorted(cols1))}. Remove {digit} from other cells in those columns.",
                            }

        # Check columns as base
        for digit in range(1, 10):
            col_positions = []
            for c in range(9):
                rows = set()
                for r in range(9):
                    if board.get_value(r, c) == 0 and digit in board.get_candidates(r, c):
                        rows.add(r)
                if 1 < len(rows) <= 2:
                    col_positions.append((c, rows))

            for i in range(len(col_positions)):
                c1, rows1 = col_positions[i]
                if len(rows1) != 2:
                    continue
                for j in range(i + 1, len(col_positions)):
                    c2, rows2 = col_positions[j]
                    if rows1 == rows2:
                        eliminated = []
                        for r in rows1:
                            for c in range(9):
                                if c in (c1, c2):
                                    continue
                                if board.get_value(r, c) == 0 and digit in board.get_candidates(r, c):
                                    board.remove_candidate(r, c, digit)
                                    eliminated.append((r, c, digit))
                        if eliminated:
                            return {
                                "type": "X-Wing (Columns)",
                                "digit": digit,
                                "cols": (c1, c2),
                                "rows": tuple(sorted(list(rows1))),
                                "candidates_removed": eliminated,
                                "explanation": f"Digit {digit} forms an X-Wing on columns {c1 + 1} and {c2 + 1} in rows {', '.join(str(x+1) for x in sorted(rows1))}. Remove {digit} from other cells in those rows.",
                            }

        return None
