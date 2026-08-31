import copy

class Game_rules:
    MILLS = [ (0, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10 ,11), (12, 13, 14), (15, 16 ,17),
              (18, 19, 20), (21, 22, 23), (0, 9, 21), (3, 10, 18), (6, 11, 15), (1, 4, 7),
              (16, 19, 22), (8, 12, 17), (5, 13, 20), (2, 14, 23)]

    ADJACENT = { 0: [1, 9], 1: [0, 2 ,4], 2: [1, 14], 3: [10, 4], 4: [1, 3, 7, 5],
                 5: [4, 13], 6: [11, 7], 7: [6, 4, 8], 8: [7, 12], 9:[0, 10, 21],
                 10: [9, 3, 11, 18], 11: [10, 6, 15], 12: [8, 13, 17], 13: [12, 5, 14, 20],
                 14: [13, 2, 23], 15: [11, 16], 16: [15, 19, 17], 17: [16, 12], 
                 18: [10, 19], 19: [18, 16, 20, 22], 20: [19, 13], 21: [9, 22],
                 22: [21, 19, 23], 23: [22, 14]}

    NOTATION = {
        0: "a7", 1: "d7", 2: "g7",
        3: "b6", 4: "d6", 5: "f6",
        6: "c5", 7: "d5", 8: "e5",
        9: "a4", 10: "b4", 11: "c4",
        12: "e4", 13: "f4", 14: "g4",
        15: "c3", 16: "d3", 17: "e3",
        18: "b2", 19: "d2", 20: "f2",
        21: "a1", 22: "d1", 23: "g1"
    }

    def __init__(self):
        # 0 = empty, 1 = player 1, 2 = player 2
        self.board = [0] * 24
        self.current_player = 1
        self.unplaced_men = {1: 9, 2: 9}
        self.placed_men = {1: 0, 2: 0}
        self.remove = False
        self.draw_limit = 10
        self.move_history = []
        self.pending_move_notation = ""

    def switch_player(self):
        self.current_player = 2 if self.current_player == 1 else 1

#functions for phase 1
    def valid_placement(self, position):
        if self.board[position] != 0:
            return False
        return True

    def mill_formed(self, position, player=None):
        if player is None:
            player = self.current_player

        for mill in self.MILLS:
            if position in mill:
                a, b, c = mill
                if self.board[a] == player and self.board[b] == player and self.board[c] == player:
                    return True
        return False

#function checks if you have a possibility to place a man then checks for a mill
    def place_man(self, position):
        if not self.valid_placement(position):
            return False

        if self.unplaced_men[self.current_player] <= 0:
            return False

        if self.remove:
            return False

        self.board[position] = self.current_player
        self.unplaced_men[self.current_player] -= 1
        self.placed_men[self.current_player] += 1

        notation = self.NOTATION[position]
        if self.mill_formed(position):
            self.remove = True
            self.pending_move_notation = notation
        else:
            self.move_history.append({"player": self.current_player, "text": notation})
            self.switch_player()

        return True

#function checks if you have a possibility to remove a man
    def valid_removal(self, position):
        opponent = 2 if self.current_player == 1 else 1
        if self.board[position] != opponent:
            return False

        if  not self.mill_formed(position, opponent):
            return True

#here it checks for "all in a mill" exception, " You may not take a man that is part of an opponent's mill unless every enemy man on the board is in a mill, in which case any of them may be taken."
        for i in range(24):
            if self.board[i] == opponent and not self.mill_formed(i, opponent):
                return False

        return True

    def remove_man(self, position):
        if not self.remove:
            return False

        if not self.valid_removal(position):
            return False

        opponent = 2 if self.current_player == 1 else 1
        self.board[position] = 0
        self.remove = False
        self.placed_men[opponent] -= 1
        full_notation = f"{self.pending_move_notation},{self.NOTATION[position]}" if self.pending_move_notation else f"x{self.NOTATION[position]}"
        self.move_history.append({"player": self.current_player, "text": full_notation})
        self.pending_move_notation = ""

        if self.check_for_win() is None:
            self.switch_player()

        return True

#functions for phase 2 and 3
    def valid_move(self, start, end, player=None):
        if player is None:
            player = self.current_player

        if self.board[start] != player:
            return False

        if self.board[end] != 0:
            return False

        if self.placed_men[player] > 3 and end not in self.ADJACENT[start]:
            return False

        return True

    def move_man(self, start, end):
        if self.remove:
            return False

        if not self.valid_move(start, end):
            return False

        if self.unplaced_men[self.current_player] > 0:
            return False

        self.board[start] = 0
        self.board[end] = self.current_player

#decided to implement the three piece draw limit rule
        if self.placed_men[1] == 3 and self.placed_men[2] == 3:
            self.draw_limit -= 1

        notation = f"{self.NOTATION[start]}-{self.NOTATION[end]}"
        if self.mill_formed(end):
            self.remove = True
            self.pending_move_notation = notation
        else:
            self.move_history.append({"player": self.current_player, "text": notation})
            self.switch_player()
        
        return True

    def trapped(self, player):
        if self.placed_men[player] == 3: #for flying, phase 3
            return 0 not in self.board

        for start in range(24):
            if self.board[start] == player:
                for end in self.ADJACENT[start]:
                    if self.valid_move(start, end, player=player):
                        return False

        return True

    def check_for_win(self):
        opponent = 2 if self.current_player == 1 else 1

        if self.unplaced_men[self.current_player] != 0 or self.unplaced_men[opponent] != 0:
            return None
        
        if self.placed_men[opponent] < 3:
            return self.current_player

        if self.trapped(opponent):
            return self.current_player

        if self.draw_limit <= 0:
            return 0  #  for draw

        return None

    #functions for ai algorithm
    def clone(self):
        return copy.deepcopy(self)

    def all_valid_moves(self):
        if self.remove:
            return [position for position in range(24) if self.valid_removal(position)]

        if self.unplaced_men[self.current_player] > 0:
            return [position for position in range(24) if self.valid_placement(position)]

        moves = []
        for start in range(24):
            if self.board[start] == self.current_player:
                if self.placed_men[self.current_player] == 3:
                    targets = range(24)
                else:
                    targets = self.ADJACENT[start]
                for end in targets:
                    if self.valid_move(start, end):
                        moves.append((start, end))
        return moves