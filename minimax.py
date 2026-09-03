import math

from move_generator import apply_move, is_game_over
from heuristics import Heuristics


class Minimax:
    def __init__(self, max_depth=3, heuristics=None):
        self.max_depth = max_depth
        self.heuristics = heuristics if heuristics else Heuristics()
        self.ai_player = None

    def best_move(self, game):
        self.ai_player = game.current_player

        best_score = -math.inf
        best = None

        for move in game.all_valid_moves():
            child = apply_move(game, move)
            maximizing_next = (child.current_player == self.ai_player)
            score = self.minimax(child, self.max_depth - 1, maximizing_next)

            if score > best_score:
                best_score = score
                best = move

        return best


    def minimax(self, game, depth, maximizing_player):
        if depth == 0 or is_game_over(game):
            return self.leaf_value(game, depth)

        moves = game.all_valid_moves()
        if len(moves) == 0:
            return self.leaf_value(game, depth)

        if maximizing_player:
            best_score = -math.inf
            for move in moves:
                child = apply_move(game, move)
                maximizing_next = (child.current_player == self.ai_player)
                score = self.minimax(child, depth - 1, maximizing_next)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = math.inf
            for move in moves:
                child = apply_move(game, move)
                maximizing_next = (child.current_player == self.ai_player)
                score = self.minimax(child, depth - 1, maximizing_next)
                best_score = min(best_score, score)
            return best_score


    def leaf_value(self, game, depth):
        score = self.heuristics.evaluate(game, self.ai_player)

        if score >= self.heuristics.WIN:
            return score + depth
        if score <= -self.heuristics.WIN:
            return score - depth
        return score

    choose_move = best_move