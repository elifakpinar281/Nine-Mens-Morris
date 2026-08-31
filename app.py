from flask import Flask, jsonify, request, send_from_directory
from game_rules import Game_rules

app = Flask(__name__, static_folder='frontend', static_url_path='')
game = Game_rules()

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
        "moveHistory": game.move_history
    }

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/api/state', methods=['GET'])
def state():
    return jsonify(get_game_state())

@app.route('/api/reset', methods=['POST'])
def reset():
    global game
    game = Game_rules()
    return jsonify(get_game_state())

@app.route('/api/action', methods=['POST'])
def action():
    data = request.get_json(force=True) or {}
    action_type = data.get('type')

    if game.check_for_win() is not None:
        return jsonify({"ok": False, **get_game_state()})

    ok = False
    if action_type == 'place':
        ok = game.place_man(data.get('position'))
    elif action_type == 'remove':
        ok = game.remove_man(data.get('position'))
    elif action_type == 'move':
        ok = game.move_man(data.get('start'), data.get('end'))

    return jsonify({"ok": ok, **get_game_state()})

if __name__ == '__main__':
    app.run(port=3000, debug=True)