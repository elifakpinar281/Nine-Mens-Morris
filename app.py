from flask import Flask, jsonify, request, send_from_directory
from game_rules import Game_rules
from alpha_beta_pruning import AlphaBetaPruning
from minimax import Minimax

app = Flask(__name__, static_folder='frontend', static_url_path='')

AI_PLAYER = 2

AVAILABLE_ALGORITHMS = {
    "alpha_beta": {
        "label": "Alpha-Beta-Pruning",
        "class": AlphaBetaPruning,
        "kwargs": {"max_depth": 4}
    },
    "minimax": {
        "label": "Minimax",
        "class": Minimax,
        "kwargs": {"max_depth": 3}
    }
}

DEFAULT_ALGORITHM = "alpha_beta"

game = Game_rules()
selected_algorithm = DEFAULT_ALGORITHM

def build_ai(algorithm_key):
    config = AVAILABLE_ALGORITHMS.get(algorithm_key, AVAILABLE_ALGORITHMS[DEFAULT_ALGORITHM])
    ai_class = config["class"]
    kwargs = config.get("kwargs", {})
    return ai_class(**kwargs)

ai_instance = build_ai(selected_algorithm)


def compute_targets():
    if game.remove:
        return {"mode": "remove", "positions": [p for p in range(24) if game.valid_removal(p)]}

    if game.unplaced_men[game.current_player] > 0:
        return {"mode": "place", "positions": [p for p in range(24) if game.valid_placement(p)]}

    return {"mode": "move", "moves": game.all_valid_moves()}

def get_game_state():
    return {
        "board": game.board,
        "currentPlayer": game.current_player,
        "unplacedMen": game.unplaced_men,
        "placedMen": game.placed_men,
        "remove": game.remove,
        "winner": game.check_for_win(),
        "targets": compute_targets(),
        "moveHistory": game.move_history,
        "mills": getattr(game, 'mills', {1: 0, 2: 0}),
        "aiPlayer": AI_PLAYER,
        "selectedAlgorithm": selected_algorithm,
    }

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/api/algorithms', methods=['GET'])
def algorithms():
    return jsonify({
        "algorithms": [
            {"key": key, "label": cfg["label"]} for key, cfg in AVAILABLE_ALGORITHMS.items()
        ],
        "selected": selected_algorithm
    })

@app.route('/api/state', methods=['GET'])
def state():
    return jsonify(get_game_state())

@app.route('/api/reset', methods=['POST'])
def reset():
    global game, selected_algorithm, ai_instance
    data = request.get_json(silent=True) or {}
    algorithm_key = data.get('algorithm', selected_algorithm)
    if algorithm_key not in AVAILABLE_ALGORITHMS:
        algorithm_key = DEFAULT_ALGORITHM

    selected_algorithm = algorithm_key
    game = Game_rules()
    ai_instance = build_ai(algorithm_key)
    return jsonify(get_game_state())

@app.route('/api/action', methods=['POST'])
def action():
    data = request.get_json(force=True) or {}
    action_type = data.get('type')

    if game.check_for_win() is not None:
        return jsonify({"success": False, **get_game_state()})

    success = False
    if action_type == 'place':
        success = game.place_man(data.get('position'))
    elif action_type == 'remove':
        success = game.remove_man(data.get('position'))
    elif action_type == 'move':
        success = game.move_man(data.get('start'), data.get('end'))

    return jsonify({"success": success, **get_game_state()})

@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    if game.check_for_win() is not None:
        return jsonify({"success": False, **get_game_state()})
    if game.current_player != AI_PLAYER:
        return jsonify({"success": False, "error": "AI is not making the move", **get_game_state()})
    move = ai_instance.choose_move(game)
    if move is None:
        return jsonify({"success": False, "error": "Could not find move", **get_game_state()})

    success = False
    if game.remove:
        success = game.remove_man(move)
    elif game.unplaced_men[game.current_player] > 0:
        success = game.place_man(move)
    else:
        success = game.move_man(*move)

    return jsonify({"success": success, **get_game_state()})

if __name__ == '__main__':
    app.run(port=3000, debug=True)