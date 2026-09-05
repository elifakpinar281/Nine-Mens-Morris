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

def is_game_over(game):
    return game.check_for_win() is not None

def get_winner(game):
    """
    Returns 1 if player 1 has won, 2 if player 2 has won, 0 for a draw,
    or None if the game hasn't ended yet. Only call this after checking
    is_game_over(game) is True.
    """
    return game.check_for_win()

if __name__ == "__main__":
    game = Game_rules()
    new_game = apply_move(game, 0)
    print("Placement test:", new_game.board[0] == 1)

    game2 = Game_rules()
    game2.unplaced_men = {1: 0, 2: 0}
    game2.placed_men = {1: 9, 2: 9}
    game2.board[0] = 1
    new_game2 = apply_move(game2, (0, 1))
    print("Movement test:", new_game2.board[0] == 0 and new_game2.board[1] == 1)

    game3 = Game_rules()
    game3.remove = True
    game3.board[5] = 2
    game3.current_player = 1
    game3.placed_men = {1: 9, 2: 1}
    new_game3 = apply_move(game3, 5)
    print("Removal test:", new_game3.board[5] == 0)

    successors = get_successors(game)
    print("How many possible next moves:", len(successors))

    game_fly = Game_rules()
    game_fly.unplaced_men = {1: 0, 2: 0}
    game_fly.placed_men = {1: 3, 2: 9}
    game_fly.board[0] = 1
    successors_fly = get_successors(game_fly)
    print("Flying test (should be 23):", len(successors_fly))

    game_trap = Game_rules()
    game_trap.unplaced_men = {1: 0, 2: 0}
    game_trap.placed_men = {1: 4, 2: 9}
    game_trap.board[0] = 1
    game_trap.board[1] = 2
    game_trap.board[9] = 2
    successors_trap = get_successors(game_trap)
    print("Trapped test (should be 0):", len(successors_trap))

    print("Game over test 1 (new game, should be False):", is_game_over(game))
    print("Game over test 2 (trapped, should be True):", is_game_over(game_trap))

    print("Winner test 1 (new game, should be None):", get_winner(game))
    print("Winner test 2 (trapped, opponent should win, should be 2):", get_winner(game_trap))