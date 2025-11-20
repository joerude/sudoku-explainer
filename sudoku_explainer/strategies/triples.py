from typing import Optional, Dict, Any, List, Tuple
from ..board import Board
from .base import Strategy


class NakedTriple(Strategy):
    """Finds Naked Triples in units and eliminates their candidates from other cells.

    A Naked Triple is three cells in a unit whose combined candidates are exactly
    three distinct digits; those digits can be removed from other cells in the unit.
    """

    def apply(self, board: Board) -> Optional[Dict[str, Any]]:
        # Rows
        for r in range(9):
            cells = [(r, c) for c in range(9) if board.get_value(r, c) == 0]
            res = self._find_triples_and_eliminate(board, cells, f"Row {r+1}")
            if res:
                return res

        # Columns
        for c in range(9):
            cells = [(r, c) for r in range(9) if board.get_value(r, c) == 0]
            res = self._find_triples_and_eliminate(board, cells, f"Column {c+1}")
            if res:
                return res

        # Boxes
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                cells = []
                for r in range(br, br + 3):
                    for c in range(bc, bc + 3):
                        if board.get_value(r, c) == 0:
                            cells.append((r, c))
                res = self._find_triples_and_eliminate(board, cells, f"Box starting at ({br+1},{bc+1})")
                if res:
                    return res

        return None

    def _find_triples_and_eliminate(self, board: Board, cells: List[Tuple[int, int]], unit_name: str) -> Optional[Dict[str, Any]]:
        from itertools import combinations

        # Build map from cell to candidates (as frozenset)
        cand_map = {cell: frozenset(board.get_candidates(cell[0], cell[1])) for cell in cells}

        # Consider combinations of up to three cells (1..3) but focus on triples
        for combo in combinations(cand_map.keys(), 3):
            union = set()
            for cell in combo:
                union |= set(cand_map[cell])
            if len(union) == 3:
                # Naked triple found; eliminate these digits from other cells in unit
                eliminated = []
                for other in cells:
                    if other in combo:
                        continue
                    r, c = other
                    for val in list(union):
                        if val in board.get_candidates(r, c):
                            board.remove_candidate(r, c, val)
                            eliminated.append((r, c, val))
                if eliminated:
                    return {
                        "type": "Naked Triple",
                        "cells": combo,
                        "digits": tuple(sorted(list(union))),
                        "candidates_removed": eliminated,
                        "explanation": f"In {unit_name}, cells {[(x[0]+1,x[1]+1) for x in combo]} form a Naked Triple with digits {sorted(list(union))}. Removed those digits from other cells in the unit.",
                    }
        return None
