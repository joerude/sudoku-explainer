import random

# Base puzzles
BASE_EASY = "003020600900305001001806400008102900700000008006708200002609500800203009005010300"
BASE_MEDIUM = "000000010400000000020000000000050407008000300001090000300400200050100000000806000"
BASE_HARD = "000000000000003085001020000000507000004000100090000000500000073002010000000040009"

def get_puzzles():
    return {
        "Easy": generate_variations(BASE_EASY, 10),
        "Medium": generate_variations(BASE_MEDIUM, 10),
        "Hard": generate_variations(BASE_HARD, 10)
    }

def generate_variations(base_puzzle: str, count: int) -> list[str]:
    """Generates variations of a puzzle by permuting symbols."""
    variations = set()
    variations.add(base_puzzle)
    
    while len(variations) < count:
        # Simple symbol permutation mapping
        mapping = list("123456789")
        random.shuffle(mapping)
        map_dict = {str(i+1): mapping[i] for i in range(9)}
        map_dict['0'] = '0' # Keep empty cells empty
        
        new_puzzle = "".join(map_dict[c] for c in base_puzzle)
        variations.add(new_puzzle)
        
    return list(variations)
