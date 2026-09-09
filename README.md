# Nine Men's Morris

A Python implementation of the board game **Nine Men's Morris** with a web-based user interface and several AI algorithms.

## Requirements

* Python 3
* Flask

## How to Start

1. Open a terminal in the project folder.
2. Install Flask (if not already installed):

```bash
pip install flask
```

3. Start the game:

```bash
python app.py
```

4. Open the game in your browser:

**http://127.0.0.1:3000/**

## AI Algorithms

The game provides the following AI algorithms:

* Alpha-Beta Pruning
* Minimax
* Expectimax
* Greedy

The AI algorithm can be selected in the game.

## Project Structure

```text
project/
├── app.py
├── game_rules.py
├── move_generator.py
├── heuristics.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
└── README.md
```

The detailed description of the source code, functions, heuristics, AI algorithms and team contributions is provided in the accompanying documentation.
