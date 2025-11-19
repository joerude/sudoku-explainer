from typing import Optional, Dict, Any, List, Tuple
from ..board import Board
from .base import Strategy

class NakedPair(Strategy):
    def apply(self, board: Board) -> Optional[Dict[str, Any]]:
        # Check Rows
        for r in range(9):
            if res := self._check_unit(board, [(r, c) for c in range(9)], "Row", r + 1):
                return res
        
        # Check Cols
        for c in range(9):
            if res := self._check_unit(board, [(r, c) for r in range(9)], "Column", c + 1):
                return res
                
        # Check Boxes
        for br in range(0, 9, 3):
            for bc in range(0, 9, 3):
                cells = []
                for r in range(br, br + 3):
                    for c in range(bc, bc + 3):
                        cells.append((r, c))
                if res := self._check_unit(board, cells, "Box", f"starting at ({br+1}, {bc+1})"):
                    return res
        return None

    def _check_unit(self, board: Board, cells: List[Tuple[int, int]], unit_type: str, unit_id: Any) -> Optional[Dict[str, Any]]:
        # Find cells with exactly 2 candidates
        candidates_map = {}
        for r, c in cells:
            if board.get_value(r, c) == 0:
                cands = tuple(sorted(list(board.get_candidates(r, c))))
                if len(cands) == 2:
                    if cands not in candidates_map:
                        candidates_map[cands] = []
                    candidates_map[cands].append((r, c))
        
        # Check for pairs
        for cands, pairs in candidates_map.items():
            if len(pairs) == 2:
                # Found a Naked Pair!
                val1, val2 = cands
                pair_cells = set(pairs)
                
                # Check if we can eliminate these candidates from other cells in the unit
                eliminated = []
                for r, c in cells:
                    if (r, c) not in pair_cells and board.get_value(r, c) == 0:
                        current_cands = board.get_candidates(r, c)
                        if val1 in current_cands:
                            board.remove_candidate(r, c, val1)
                            eliminated.append((r, c, val1))
                        if val2 in current_cands:
                            board.remove_candidate(r, c, val2)
                            eliminated.append((r, c, val2))
                
                if eliminated:
                    return {
                        'type': 'Naked Pair',
                        'candidates_removed': eliminated,
                        'explanation': f"In {unit_type} {unit_id}, cells {pairs[0]} and {pairs[1]} form a Naked Pair with values {val1} and {val2}. We can remove these values from other cells in the same {unit_type}."
                    }
        return None
