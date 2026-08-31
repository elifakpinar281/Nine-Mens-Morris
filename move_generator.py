from game_rules import Game_rules

def apply_move(game, move):
    new_game = game.clone()
    if game.remove:
        new_game.remove_man(move)
    elif game.unplaced_men[game.current_player] > 0:
        new_game.place_man(move)
    else:
        start, end = move
        new_game.move_man(start, end)
    return new_game

def get_successors(game):
    successors = []
    for move in game.all_valid_moves():
        next_game = apply_move(game, move)
        successors.append((move, next_game))
    return successors

if __name__ == "__main__":
    game = Game_rules()#placement
    new_game = apply_move(game, 0)
    print("Placement test:", new_game.board[0] == 1)

    game2 = Game_rules()#movement
    game2.unplaced_men = {1: 0, 2: 0}
    game2.placed_men = {1: 9, 2: 9}
    game2.board[0] = 1
    new_game2 = apply_move(game2, (0, 1))
    print("Movement test:", new_game2.board[0] == 0 and new_game2.board[1] == 1)

    game3 = Game_rules()#removal
    game3.remove = True
    game3.board[5] = 2
    game3.current_player = 1
    game3.placed_men = {1: 9, 2: 1}
    new_game3 = apply_move(game3, 5)
    print("Removal test:", new_game3.board[5] == 0)

    successors = get_successors(game)
    print("How many possible next moves:", len(successors))