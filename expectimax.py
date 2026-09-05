import math
from heuristics import Heuristics
from move_generator import apply_move, is_game_over

class Expectimax:
    def __init__(self, max_depth = 3, heuristic = None):
        self.max_depth = max_depth
        self.heuristic = heuristic if heuristic else Heuristics()
        self.ai_player = None

    def best_move(self, game):
        self.ai_player = game.current_player
        moves = game.all_valid_moves()

        if not moves:
            return None

        best_score = -math.inf
        chosen_move = moves[0]
        for move in moves:
            next_game = apply_move(game, move)
            next_max = (next_game.current_player == self.ai_player)
            score = self.expectimax(next_game, self.max_depth - 1, next_max)

            if score> best_score:
                best_score = score
                chosen_move = move

        return chosen_move

    def expectimax(self, game, depth, is_max):
        if depth == 0 or is_game_over(game):
            return self.evaluate_board(game, depth)

        moves = game.all_valid_moves()
        if len(moves) == 0:
            return self.evaluate_board(game, depth)

        if is_max: #max node for the AI player
            best_score = -math.inf
            for move in moves:
                next_game = apply_move(game,move)
                next_max = (next_game.current_player == self.ai_player)
                score = self.expectimax(next_game, depth - 1, next_max)
                best_score = max(best_score, score)
            return best_score
        else: #chance node for the human player
            expected_score = 0.0
            probability = 1.0/len(moves)
            for move in moves:
                next_game = apply_move(game, move)
                next_max = (next_game.current_player == self.ai_player)
                score = self.expectimax(next_game, depth - 1, next_max)
                expected_score += probability * score
            return expected_score

    def evaluate_board(self, game, depth):
        score = self.heuristic.evaluate(game, self.ai_player)

        if score >= self.heuristic.WIN:
            return score + depth
        if score <= -self.heuristic.WIN:
            return score - depth

        return score
    