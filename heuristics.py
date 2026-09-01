from enum import Enum

class Phase(Enum):
    PLACING = 1
    MOVING = 2
    FLYING = 3

class Heuristics:
    WIN = 100_000 # Outweighs all other heuristic values

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
        if weights is None:
            weights = self.DEFAULT_WEIGHTS
        self.weights = weights

    def evaluate(self, game, player):
        opponent = self.opponent_of(player)

        if self.is_lost(game, opponent):
            return self.WIN
        if self.is_lost(game, player):
            return -self.WIN
        if game.draw_limit <= 0:
            return 0

        weights = self.weights[self.phase_of(game, player)]

        piece_difference = self.pieces_diff(game, player) - self.pieces_diff(game, opponent)
        mills_difference = self.count_mills(game, player) - self.count_mills(game, opponent)
        two_row_difference = self.count_two_in_a_row(game, player) - self.count_two_in_a_row(game, opponent)
        position_difference = self.positional_value(game, player) - self.positional_value(game, opponent)
        mobility_difference = self.count_legal_moves(game, player) - self.count_legal_moves(game, opponent)
        swinging_difference = self.count_swinging_mills(game, player) - self.count_swinging_mills(game, opponent)
        blocked_difference = self.count_blocked_opponents(game, opponent) - self.count_blocked_opponents(game, player)
        mill_moves_difference = self.count_mill_moves(game, player) - self.count_mill_moves(game, opponent)
        own_threats = self.immediate_threats(game, player)
        opponent_threats = self.immediate_threats(game, opponent)
        multiple_threats_difference = max(0, own_threats - 1) - max(0, opponent_threats - 1)

        score = 0
        score += weights["piece_difference"] * piece_difference
        score += weights["mills"] * mills_difference
        score += weights["two_in_a_row"] * two_row_difference
        score += weights["blocked_opponent"] * blocked_difference
        score += weights["positional"] * position_difference
        score += weights["mobility"] * mobility_difference
        score += weights["swinging"] * swinging_difference
        score += weights["mill_moves"] * mill_moves_difference
        score += weights["multiple_threats"] * multiple_threats_difference
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


    # More pieces allow more aggressive play
    def pieces_diff(self, game, player):
        return game.placed_men[player] + game.unplaced_men[player]


    # More mills gives more opportunities to capture opponent pieces
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
        if game.placed_men[player] == 3:
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
        if game.unplaced_men[player] > 0:
            empties = 0
            for position in range(24):
                if game.board[position] == 0:
                    empties += 1

            return empties

        flying = game.placed_men[player] == 3
        moves = 0
        for start in range(24):
            if game.board[start] != player:
                continue

            if flying:
                for end in range(24):
                    if game.board[end] == 0:
                        moves += 1
            else:
                for end in game.ADJACENT[start]:
                    if game.board[end] == 0:
                        moves += 1
        return moves


    # Positions with more neighbours give more movement opportunities and strategic options
    def positional_value(self, game, player):
        value = 0
        for position in range(24):
            if game.board[position] == player:
                value += len(game.ADJACENT[position])

        return value

    # Encourages moving pieces between mills to repeatedly capture opponent pieces
    def count_swinging_mills(self, game, player):
        if game.placed_men[player] == 3:
            return 0

        count = 0
        for position in range(24):
            if game.board[position] != player:
                continue

            if not game.mill_formed(position, player):
                continue

            for neighbour in game.ADJACENT[position]:
                if game.board[neighbour] == 0 and self.move_forms_mill(game, position, neighbour, player):
                    count += 1
                    break

        return count

    # Counts moves that can immediately create a mill
    def count_mill_moves(self, game, player):
        count = 0
        for start in range(24):
            if game.board[start] != player:
                continue

            if game.placed_men[player] == 3:
                targets = range(24)
            else:
                targets = game.ADJACENT[start]

            for end in targets:
                if game.board[end] == 0 and self.move_forms_mill(game, start, end, player):
                    count += 1

        return count

    # During placing, it looks for positions that could complete a mill
    # During moving and flying, it looks for moves that can immediately form a mill
    def immediate_threats(self, game, player):
        if game.unplaced_men[player] > 0:
            return self.count_two_in_a_row(game, player)
        return self.count_mill_moves(game, player)

    # Checks whether moving a piece to a position would form a mill
    def move_forms_mill(self, game, start, end, player):
        for mill in game.MILLS:
            if end not in mill:
                continue
            completes = True
            for spot in mill:
                if spot == end:
                    continue

                occupant = game.board[spot]

                if spot == start:
                    occupant = 0

                if occupant != player:
                    completes = False
                    break

            if completes:
                return True
        return False

    @staticmethod
    def opponent_of(player):
        if player == 1:
            return 2
        else:
            return 1