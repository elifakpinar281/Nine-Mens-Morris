import math
from move_generator import get_successors
from heuristics import Heuristics

class Greedy:

    def __init__(self, max_depth=None, heuristics=None):
        self.heuristics = heuristics if heuristics else Heuristics()
        self.ai_player = None
        self.last_scored_moves = []  # every move + its score, from the most recent call

    def best_move(self, game):
        self.ai_player = game.current_player
        best_score = -math.inf
        best = None
        scored = []
        for move, child in get_successors(game):
            score = self.heuristics.evaluate(child, self.ai_player)
            scored.append((move, score))
            if score > best_score:
                best_score = score
                best = move
        self.last_scored_moves = scored
        return best

    choose_move = best_move