import math

from move_generator import apply_move, is_game_over
from heuristics import Heuristics

class AlphaBetaPruning:
    def __init__(self, max_depth=4, heuristics=None):
        self.max_depth = max_depth
        self.heuristics = heuristics if heuristics else Heuristics()
        self.ai_player = None

    def best_move(self, game):
        self.ai_player = game.current_player
        best_score = -math.inf
        best = None
        alpha, beta = -math.inf, math.inf #start with no bound in either direction

        moves = self.order_moves(game, game.all_valid_moves())

        for move in moves:
            child = apply_move(game, move)
            maximizing_next = (child.current_player == self.ai_player)
            score = self.alphabeta(child, self.max_depth - 1, alpha, beta, maximizing_next)

            if score > best_score:
                best_score = score
                best = move
            alpha = max(alpha, best_score)

        return best

    def alphabeta(self, game, depth, alpha, beta, maximizing_player):
        if depth == 0 or is_game_over(game): #depth limit reached or game already decided
            return self.leaf_value(game, depth)

        moves = game.all_valid_moves()
        if len(moves) == 0:
            return self.leaf_value(game, depth)

        moves = self.order_moves(game, moves)

        if maximizing_player:
            best_score = -math.inf
            for move in moves:
                child = apply_move(game, move)
                maximizing_next = (child.current_player == self.ai_player)
                score = self.alphabeta(child, depth -1 , alpha, beta, maximizing_next)
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    break
            return best_score
        else:
            best_score = math.inf
            for move in moves:
                child = apply_move(game, move)
                maximizing_next = (child.current_player == self.ai_player)
                score = self.alphabeta(child, depth - 1, alpha, beta, maximizing_next)
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if alpha >=beta:
                    break
            return best_score

    def leaf_value(self, game, depth):
        score = self.heuristics.evaluate(game, self.ai_player)
        if score >= self.heuristics.WIN:
            return score + depth
        if score <= -self.heuristics.WIN:
            return score - depth
        return score


    def order_moves(self, game, moves):
        mover = game.current_player
        scored = []
        for move in moves:
            next_game = apply_move(game, move)
            score = self.heuristics.evaluate(next_game, self.ai_player)
            scored.append((score, move))

        descending = (mover == self.ai_player)
        scored.sort(key=lambda pair: pair[0], reverse=descending)
        return [move for _, move in scored]

    choose_move = best_move
