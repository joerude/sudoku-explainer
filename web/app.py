import json
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sudoku_explainer.board import Board
from sudoku_explainer.solver import SudokuSolver
from sudoku_explainer.utils import parse_puzzle, board_to_string
from sudoku_explainer.puzzles import get_puzzles

app = FastAPI()
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Default puzzle (Hard)
    default_puzzle = "000000010400000000020000000000050407008000300001090000300400200050100000000806000"
    board = parse_puzzle(default_puzzle)
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "board": board, 
        "puzzle_str": default_puzzle,
        "history": "[]",
        "puzzles": get_puzzles(),
        "explanation": "Click 'Next Step' to start solving."
    })

@app.post("/step", response_class=HTMLResponse)
async def step(request: Request, puzzle_str: str = Form(...), history: str = Form("[]")):
    try:
        history_list = json.loads(history)
        board = parse_puzzle(puzzle_str)
        solver = SudokuSolver(board)
        step = solver.solve_step()
        
        explanation = "No more steps found or puzzle solved."
        if step:
            explanation = f"<strong>{step['type']}</strong>: {step['explanation']}"
            # Only append to history if a step was actually taken
            history_list.append(puzzle_str)
        elif board.is_solved():
            explanation = "<strong>Solved!</strong> The puzzle is complete."
        else:
            explanation = "<strong>Stuck!</strong> No logical step found."
        
        new_puzzle_str = board_to_string(board)
        
        return templates.TemplateResponse("partials/interaction_area.html", {
            "request": request,
            "board": board,
            "puzzle_str": new_puzzle_str,
            "history": json.dumps(history_list),
            "explanation": explanation
        })
    except Exception as e:
        return f"Error: {str(e)}"

@app.post("/undo", response_class=HTMLResponse)
async def undo(request: Request, history: str = Form("[]")):
    try:
        history_list = json.loads(history)
        if not history_list:
            # Should not happen if button is disabled, but handle gracefully
            return "No history to undo."
            
        prev_puzzle = history_list.pop()
        board = parse_puzzle(prev_puzzle)
        
        return templates.TemplateResponse("partials/interaction_area.html", {
            "request": request,
            "board": board,
            "puzzle_str": prev_puzzle,
            "history": json.dumps(history_list),
            "explanation": "Undid last step."
        })
    except Exception as e:
        return f"Error undoing: {str(e)}"

@app.post("/new", response_class=HTMLResponse)
async def new_puzzle(request: Request, puzzle_input: str = Form(...)):
    try:
        # Basic validation
        clean_input = "".join(c for c in puzzle_input if c.isdigit())
        if len(clean_input) < 81:
             clean_input = clean_input.ljust(81, '0')
        elif len(clean_input) > 81:
            clean_input = clean_input[:81]
            
        board = parse_puzzle(clean_input)
        return templates.TemplateResponse("partials/interaction_area.html", {
            "request": request,
            "board": board,
            "puzzle_str": clean_input,
            "history": "[]",
            "explanation": "New puzzle loaded."
        })
    except Exception as e:
        return f"Error loading puzzle: {str(e)}"
