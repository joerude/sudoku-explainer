# Sudoku Explainer

A Python-based Sudoku solver and explainer that uses logical strategies to solve puzzles step-by-step, providing human-readable explanations.

## Features

- **Step-by-Step Explanations**: Understand *why* a number goes in a cell.
- **Strategies Implemented**:
    - Naked Single
    - Hidden Single
    - Naked Pair
- **Web Interface**:
    - Modern, dark-themed UI.
    - Interactive board with candidate visualization.
    - "Easy Mode" (Hide Notes) for a cleaner look.
    - Undo functionality.
    - Sample puzzles (Easy, Medium, Hard).
- **CLI**: Run the solver from the command line.

## Installation

This project uses `uv` for dependency management.

1.  **Install `uv`** (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Install Dependencies**:
    ```bash
    uv pip install -r requirements.txt
    ```

## Usage

### Web Interface

Start the web server:

```bash
python3 -m uvicorn web.app:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

### CLI

Run the solver on a specific puzzle:

```bash
python3 main.py --puzzle "YOUR_81_CHAR_PUZZLE_STRING"
```

## Docker Usage

You can run the Sudoku Explainer app in a container without installing system dependencies on your host.

### Build the Docker image

```bash
docker build -t sudoku-explainer .
```

### Run the web interface

```bash
docker run --rm -p 8000:8000 sudoku-explainer
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

### Run the CLI

To run the CLI solver inside the container:

```bash
docker run --rm sudoku-explainer python main.py --puzzle "YOUR_81_CHAR_PUZZLE_STRING"
```

#### Run with live logs

To see live logs and errors directly in your terminal, run:

```bash
docker run --rm -it -p 8000:8000 sudoku-explainer
```

This will show all output from the app in real time. If you want to see logs for a running container, you can also use:

```bash
docker logs -f <container_id>
```

But with `--rm` and `-it`, you will see logs as they happen.

## Development

### Linting and Formatting

```bash
ruff check .
ruff format .
```
