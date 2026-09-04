from enum import Enum
from game_rules import Game_rules

class Phase(Enum):
    PLACING = 1
    MOVING = 2
    FLYING = 3

class Heuristics:
    # Winning or losing positions is always more important than any heuristic value
    WIN = 100_000

    DEFAULT_WEIGHTS = {
        Phase.PLACING: {
            "piece_difference": 35,
            "mills": 15,
            "two_in_a_row": 12,
            "blocked_opponent": 6,
            "positional": 3,
            "mobility": 0,
            "swinging": 0,
            "mill_moves": 0,
            "multiple_threats": 12
        },
        Phase.MOVING: {
            "piece_difference": 40,
            "mills": 12,
            "two_in_a_row": 10,
            "blocked_opponent": 12,
            "positional": 2,
            "mobility": 6,
            "swinging": 45,
            "mill_moves": 15,
            "multiple_threats": 15
        },
        Phase.FLYING: {
            "piece_difference": 40,
            "mills": 10,
            "two_in_a_row": 22,
            "blocked_opponent": 0,
            "positional": 0,
            "mobility": 6,
            "swinging": 0,
            "mill_moves": 25,
            "multiple_threats": 30
        }
    }

    def __init__(self, weights=None):
        if weights is None: # use default weights if no custom weights provided
            weights = self.DEFAULT_WEIGHTS
        self.weights = weights

        # stores the mills for each board position to avoid checking all mills every time
        self.mills_by_position = {}
        for point in range(24):
            mills = []
            for mill in Game_rules.MILLS:
                if point in mill:
                    mills.append(mill)
            self.mills_by_position[point] = mills

    def evaluate(self, game, player):
        opponent = self.opponent_of(player)

        # Handle terminal positions before calculating heuristic value
        if self.is_lost(game, opponent):
            return self.WIN
        if self.is_lost(game, player):
            return -self.WIN
        if game.draw_limit <= 0: # draw has same value for both players
            return 0

        # Each player is scored with the weights of their own phase -> players can be in different phases
        player_weights = self.weights[self.phase_of(game, player)]
        opponent_weights = self.weights[self.phase_of(game, opponent)]
        player_score = self.own_score(game, player, opponent, player_weights)
        opponent_score = self.own_score(game, opponent, player, opponent_weights)

        # Calculate difference between both scores
        return player_score - opponent_score


    # Weighted sum of one player's own features
    def own_score(self, game, player, opponent, weights):
        two_in_a_row = self.count_two_in_a_row(game, player)
        mill_moves = None

        features = {
            "piece_difference": self.pieces_diff(game, player),
            "mills": self.count_mills(game, player),
            "two_in_a_row": two_in_a_row,
            "positional": self.positional_value(game, player),
            "blocked_opponent": self.count_blocked_opponents(game, opponent), # blocked opponents is better for the player
            "mobility": 0,
            "swinging": 0,
            "mill_moves": 0,
        }

        # These might be weighted 0 in a given phase -> only compute when they actually matter
        if weights["mobility"]:
            features["mobility"] = self.count_legal_moves(game, player)

        if weights["swinging"]:
            features["swinging"] = self.count_swinging_mills(game, player)

        if weights["mill_moves"]:
            mill_moves = self.count_mill_moves(game, player)
            features["mill_moves"] = mill_moves

        threats = self.threats(game, player, two_in_a_row, mill_moves)
        features["multiple_threats"] = max(0, threats - 1)

        score = 0
        for name, value in features.items(): # combine all features with their weights
            score += weights[name] * value
        return score


    def phase_of(self, game, player):
        if game.unplaced_men[player] > 0:
            return Phase.PLACING

        if game.placed_men[player] == 3:
            return Phase.FLYING

        return Phase.MOVING

    def is_lost(self, game, player):
        placed_all = game.unplaced_men[player] == 0
        if not placed_all:
            return False

        if game.placed_men[player] < 3:
            return True
        if game.trapped(player):
            return True
        return False

    @staticmethod
    def opponent_of(player):
        if player == 1:
            return 2
        else:
            return 1

    # More pieces give more opportunities to create mills
    def pieces_diff(self, game, player):
        return game.placed_men[player] + game.unplaced_men[player]


    # More mills give more opportunities to capture opponent pieces
    def count_mills(self, game, player):
        count = 0
        for a, b, c in game.MILLS:
            if game.board[a] == player and game.board[b] == player and game.board[c] == player:
                count += 1

        return count

    # Counts potential mills where two pieces are already placed
    def count_two_in_a_row(self, game, player):
        count = 0
        for a, b, c in game.MILLS:
            line = (game.board[a], game.board[b], game.board[c])
            if line.count(player) == 2 and line.count(0) == 1:
                count += 1

        return count

    # More blocked opponent pieces restrict the opponent's movement
    def count_blocked_opponents(self, game, player):
        if game.placed_men[player] == 3: # flying pieces cannot be blocked
            return 0
        count = 0
        for position in range(24):
            if game.board[position] != player:
                continue

            has_free_neighbour = False
            for neighbour in game.ADJACENT[position]:
                if game.board[neighbour] == 0:
                    has_free_neighbour = True
                    break
            if not has_free_neighbour:
                count += 1
        return count

    # More legal moves give more flexibility and strategic options
    def count_legal_moves(self, game, player):
        if game.unplaced_men[player] > 0: # placing -> every empty position reachable
            empties = 0
            for position in range(24):
                if game.board[position] == 0:
                    empties += 1

            return empties

        flying = game.placed_men[player] == 3 # flying -> every empty position reachable
        moves = 0
        for start in range(24):
            if game.board[start] != player:
                continue

            if flying:
                for end in range(24):
                    if game.board[end] == 0:
                        moves += 1
            else:
                for end in game.ADJACENT[start]: # moving -> only adjacent empty positions reachable
                    if game.board[end] == 0:
                        moves += 1
        return moves


    # Positions with more neighbours give more movement options
    def positional_value(self, game, player):
        value = 0
        for position in range(24):
            if game.board[position] == player:
                value += len(game.ADJACENT[position])

        return value

    # Count pieces that can move between mills to repeatedly capture opponent pieces
    def count_swinging_mills(self, game, player):
        if game.placed_men[player] == 3:
            return 0

        count = 0
        for position in range(24):
            if game.board[position] != player:
                continue

            if not game.mill_formed(position, player): # piece must currently be part of a mill
                continue

            # Check whether it can move to an adjacent position to form another mill
            for neighbour in game.ADJACENT[position]:
                if game.board[neighbour] == 0 and self.move_forms_mill(game, position, neighbour, player):
                    count += 1
                    break

        return count

    # Counts moves that immediately create a mill
    def count_mill_moves(self, game, player):
        count = 0
        for start in range(24):
            if game.board[start] != player:
                continue

            if game.placed_men[player] == 3:
                targets = range(24) # flying pieces can move to any empty position
            else:
                targets = game.ADJACENT[start]

            for end in targets:
                if game.board[end] == 0 and self.move_forms_mill(game, start, end, player):
                    count += 1

        return count

    # During placing, a two_in_a_row is a potential mill
    # After placing, a mill move is an immediate threat
    def threats(self, game, player, two_in_a_row, mill_moves):
        if game.unplaced_men[player] > 0:
            return two_in_a_row
        if mill_moves is None:
            mill_moves = self.count_mill_moves(game, player)
        return mill_moves

    # Checks whether moving a piece from start to end would form a mill
    def move_forms_mill(self, game, start, end, player):
        # Only mills that contain the end position are checked
        for mill in self.mills_by_position[end]:
            completes = True
            for point in mill:
                if point == end:
                    continue

                owner = game.board[point]
                if point == start: # start position becomes empty after move
                    owner = 0

                if owner != player:
                    completes = False
                    break
            if completes:
                return True
        return False