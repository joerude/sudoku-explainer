from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from ..board import Board

class Strategy(ABC):
    @abstractmethod
    def apply(self, board: Board) -> Optional[Dict[str, Any]]:
        """
        Applies the strategy to the board.
        Returns a dictionary with details of the move if successful, else None.
        The dictionary should contain:
        - 'type': Strategy name
        - 'row': Row index (if applicable)
        - 'col': Column index (if applicable)
        - 'value': Value placed (if applicable)
        - 'candidates_removed': List of (row, col, value) tuples (if applicable)
        - 'explanation': Human-readable string
        """
        pass
