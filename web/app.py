import json
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from sudoku_explainer.board import Board
from sudoku_explainer.solver import SudokuSolver
from sudoku_explainer.utils import (
    parse_puzzle,
    board_to_string,
    solve_sudoku_backtracking,
)
from sudoku_explainer.puzzles import get_puzzles
from sudoku_explainer.ocr import process_sudoku_image

app = FastAPI()
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")


def get_solution_str(puzzle_str: str) -> str:
    board = parse_puzzle(puzzle_str)
    # Try to solve logically first to reduce search space
    solver = SudokuSolver(board)
    for _ in solver.solve():
        pass  # Just run it until solved or stuck

    # Then finish with backtracking
    solve_sudoku_backtracking(board)
    return board_to_string(board)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Default puzzle (Hard)
    default_puzzle = "000000010400000000020000000000050407008000300001090000300400200050100000000806000"
    board = parse_puzzle(default_puzzle)
    solution_str = get_solution_str(default_puzzle)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "board": board,
            "puzzle_str": default_puzzle,
            "original_puzzle_str": default_puzzle,
            "solution_str": solution_str,
            "history": "[]",
            "puzzles": get_puzzles(),
            "explanation": "Click 'Next Step' to start solving.",
        },
    )


@app.post("/step", response_class=HTMLResponse)
async def step(
    request: Request,
    puzzle_str: str = Form(...),
    original_puzzle_str: str = Form(...),
    history: str = Form("[]"),
):
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
        solution_str = get_solution_str(original_puzzle_str)

        return templates.TemplateResponse(
            "partials/update_response.html",
            {
                "request": request,
                "board": board,
                "puzzle_str": new_puzzle_str,
                "original_puzzle_str": original_puzzle_str,
                "solution_str": solution_str,
                "history": json.dumps(history_list),
                "explanation": explanation,
            },
        )
    except Exception as e:
        return f"Error: {str(e)}"


@app.post("/update", response_class=HTMLResponse)
async def update_board(
    request: Request,
    puzzle_str: str = Form(...),
    original_puzzle_str: str = Form(...),
    history: str = Form("[]"),
    row: int = Form(...),
    col: int = Form(...),
    value: int = Form(...),
    mode: str = Form(...),  # 'value' or 'note'
):
    try:
        history_list = json.loads(history)
        board = parse_puzzle(puzzle_str)

        # Check if trying to modify a fixed cell
        idx = row * 9 + col
        if mode == "value" and original_puzzle_str[idx] != "0":
            # Ignore update for fixed cells
            pass
        else:
            # Save current state to history before modifying if it's a value change
            if mode == "value":
                history_list.append(puzzle_str)

            if mode == "value":
                if value == 0:
                    board.grid[row][col] = 0
                else:
                    board.set_value(row, col, value)
            elif mode == "note":
                if value != 0:
                    if value in board.candidates[row][col]:
                        board.remove_candidate(row, col, value)
                    else:
                        board.add_candidate(row, col, value)

        new_puzzle_str = board_to_string(board)
        solution_str = get_solution_str(original_puzzle_str)

        return templates.TemplateResponse(
            "partials/update_response.html",
            {
                "request": request,
                "board": board,
                "puzzle_str": new_puzzle_str,
                "original_puzzle_str": original_puzzle_str,
                "solution_str": solution_str,
                "history": json.dumps(history_list),
                "explanation": "Manual update.",
                "selected_row": row,
                "selected_col": col,
            },
        )
    except Exception as e:
        return f"Error updating: {str(e)}"


@app.post("/undo", response_class=HTMLResponse)
async def undo(
    request: Request, history: str = Form("[]"), original_puzzle_str: str = Form(...)
):
    try:
        history_list = json.loads(history)
        if not history_list:
            return "No history to undo."

        prev_puzzle = history_list.pop()
        board = parse_puzzle(prev_puzzle)
        solution_str = get_solution_str(original_puzzle_str)

        return templates.TemplateResponse(
            "partials/update_response.html",
            {
                "request": request,
                "board": board,
                "puzzle_str": prev_puzzle,
                "original_puzzle_str": original_puzzle_str,
                "solution_str": solution_str,
                "history": json.dumps(history_list),
                "explanation": "Undid last step.",
            },
        )
    except Exception as e:
        return f"Error undoing: {str(e)}"


@app.post("/new", response_class=HTMLResponse)
async def new_puzzle(request: Request, puzzle_input: str = Form(...)):
    try:
        # Basic validation
        clean_input = "".join(c for c in puzzle_input if c.isdigit())
        if len(clean_input) < 81:
            clean_input = clean_input.ljust(81, "0")
        elif len(clean_input) > 81:
            clean_input = clean_input[:81]

        board = parse_puzzle(clean_input)
        solution_str = get_solution_str(clean_input)

        return templates.TemplateResponse(
            "partials/update_response.html",
            {
                "request": request,
                "board": board,
                "puzzle_str": clean_input,
                "original_puzzle_str": clean_input,
                "solution_str": solution_str,
                "history": "[]",
                "explanation": "New puzzle loaded.",
            },
        )
    except Exception as e:
        return f"Error loading puzzle: {str(e)}"


@app.post("/import", response_class=HTMLResponse)
async def import_puzzle(request: Request, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        puzzle_str, error = process_sudoku_image(contents)

        if error:
            return f"Error processing image: {error}"

        # Validate length
        if len(puzzle_str) != 81:
            return f"Error: Detected {len(puzzle_str)} digits, expected 81."

        board = parse_puzzle(puzzle_str)
        solution_str = get_solution_str(puzzle_str)

        return templates.TemplateResponse(
            "partials/update_response.html",
            {
                "request": request,
                "board": board,
                "puzzle_str": puzzle_str,
                "original_puzzle_str": puzzle_str,
                "solution_str": solution_str,
                "history": "[]",
                "explanation": "Imported from image.",
            },
        )
    except Exception as e:
        print(f"Upload error: {e}")
        # Return a valid response even on error so the UI doesn't break
        # We'll use a dummy board or the current one if we had access to it, but here we don't.
        # Let's return an empty board with the error message.
        empty_board = Board()
        return templates.TemplateResponse(
            "partials/update_response.html",
            {
                "request": request,
                "board": empty_board,
                "puzzle_str": "0" * 81,
                "original_puzzle_str": "0" * 81,
                "solution_str": "0" * 81,
                "history": "[]",
                "explanation": f"<strong>Error:</strong> {str(e)}",
            },
        )
