from board import Board
import operator


class two_step_check_Player():
    def __init__(self):
        self.side = -1

    def set_side(self, side):
        self.side = side

    def possible_move(self, board, side):
        test = Board(state=board.encode_state(), previous_state=board.encode_previous_state())
        if board.game_over():
            return []
        possible_placements = []
        for i in range(5):
            for j in range(5):
                if test.is_valid_move(i, j, side):
                    possible_placements.append((i, j))
        return possible_placements

    def on_edge(self, move):
        if move[0] == 0 or move[0] == 4 or move[1] == 0 or move[1] == 4:
            return True
        return False

    def select_best_move(self, possible_placements, board):
        move = {}
        win = False
        for movement in possible_placements:
            move[movement] = 0
            new_board = Board(state=board.encode_state(), previous_state=board.encode_previous_state())
            new_board.move(movement[0], movement[1], self.side)
            opp_died_pieces = new_board.get_died_pieces()
            if new_board.game_over():
                win = True
                win_move = movement
                break
            if opp_died_pieces:
                move[movement] += 5 * len(opp_died_pieces)
            if self.on_edge(movement):
                move[movement] -= 1
            liberties = 0.1 * new_board.cal_liberties(self.side)
            move[movement] += liberties
            opp_next_move_reward = self.opp_next_score(new_board)
            move[movement] -= opp_next_move_reward
        if win:
            return win_move
        return max(move.items(), key=operator.itemgetter(1))[0]

    def opp_next_score(self, board):
        possible_placements = self.possible_move(board, 3-self.side)
        score = 0
        if possible_placements:
            val = [0]*len(possible_placements)
            for i in range(len(possible_placements)):
                new_board = Board(state=board.encode_state(), previous_state=board.encode_previous_state())
                new_board.move(possible_placements[i][0], possible_placements[i][1], 3-self.side)
                opp_died_pieces = new_board.get_died_pieces()
                if new_board.game_over():
                    val[i] = 999
                    break
                if opp_died_pieces:
                    val[i] += 5 * len(opp_died_pieces)
                if self.on_edge(possible_placements[i]):
                    val[i] -= 1
                liberties = 0.1 * new_board.cal_liberties(self.side)
                val[i] += liberties
            score = max(val)
        return score


    def move(self, board):
        if board.game_over():
            return
        possible_placements = self.possible_move(board, self.side)
        if not possible_placements:
            return 'PASS'
        else:
            i, j = self.select_best_move(possible_placements, board)
            board.move(i, j, self.side)
            return (i,j)

    def learn(self, board):
        return

class MinimaxPlayer():
    def __init__(self):
        self.side = -1

    def set_side(self, side):
        self.side = side

    def possible_move(self,board, side):
        test = Board(state=board.encode_state(), previous_state=board.encode_previous_state())
        if board.game_over():
            return []
        possible_placements = []
        for i in range(5):
            for j in range(5):
                if test.is_valid_move(i, j, side):
                    possible_placements.append((i, j))
        return possible_placements

    def on_edge(self, move):
        if move[0] == 0 or move[0] == 4 or move[1] == 0 or move[1] == 4:
            return True
        return False

    def move(self, board):
        if board.game_over():
            return
        possible_placements = self.possible_move(board, self.side)
        if not possible_placements:
            return 'PASS'
        else:
            i, j = self.select_best_move(possible_placements, board)
            board.move(i, j, self.side)
            return (i, j)

    def select_best_move(self, possible_placements, board):
        move = {}
        win = False
        for movement in possible_placements:
            move[movement] = 0
            new_board = Board(state=board.encode_state(), previous_state=board.encode_previous_state())
            new_board.move(movement[0], movement[1], self.side)
            opp_died_pieces = new_board.get_died_pieces()
            if new_board.game_over():
                win = True
                win_move = movement
                break
            if opp_died_pieces:
                move[movement] += 10 * len(opp_died_pieces)
            if self.on_edge(movement):
                move[movement] -= 3
            liberties = 0.5 * new_board.cal_liberties(self.side)
            move[movement] += liberties
            move[movement] += self.linked(board, movement)
            move[movement] += self.detect_potential_to_make_eye(new_board, movement, self.side)
            minimax_val = self.minimax_alg(new_board, 2, 3 - self.side)
            move[movement] -= minimax_val
        if win:
            return win_move
        return max(move.items(), key=operator.itemgetter(1))[0]


    def linked(self, board, move):
        allies = board.detect_neighbor_ally(board.state, move[0], move[1])
        if allies:
            if len(allies) > 2:
                return -1
            return len(allies)
        else:
            return 0

    def minimax_alg(self, board, depth, side):
        if depth == 0:
            return 0
        possible_placements = self.possible_move(board, side)
        score = 0
        if possible_placements:
            val = [0] * len(possible_placements)
            for i in range(len(possible_placements)):
                new_board = Board(state=board.encode_state(), previous_state=board.encode_previous_state())
                new_board.move(possible_placements[i][0], possible_placements[i][1], side)
                opp_died_pieces = new_board.get_died_pieces()
                if new_board.game_over():
                    val[i] = 999
                    break
                if opp_died_pieces:
                    val[i] += 5 * len(opp_died_pieces)
                if self.on_edge(possible_placements[i]):
                    val[i] -= 1
                liberties = 0.1 * new_board.cal_liberties(self.side)
                val[i] += liberties
                val[i] += self.linked(board, possible_placements[i])
                val[i] += 0.1*self.detect_potential_to_make_eye(new_board, possible_placements[i], self.side)
                val[i] -= self.minimax_alg(new_board, depth-1, 3 - side)
            score = max(val)
        return score

    def detect_potential_to_make_eye(self, board, move, side):
        score = 0
        possible_eyes = []
        if move[0] != 0 and board.state[move[0]-1][move[1]] == 0:
            possible_eyes.append((move[0]-1,move[1]))
        if move[1] != 0 and board.state[move[0]][move[1]-1] == 0:
            possible_eyes.append((move[0], move[1] - 1))
        if move[0] != 4 and board.state[move[0]+1][move[1]] == 0:
            possible_eyes.append((move[0] + 1, move[1]))
        if move[1] != 4 and board.state[move[0]][move[1]+1] == 0:
            possible_eyes.append((move[0], move[1] + 1))
        if possible_eyes:
            for eye in possible_eyes:
                if not board.is_valid_move(eye[0],eye[1], 3-side):
                    score += 1
        return score

def print_move(move):
    f = open('output.txt', 'w')
    if move =='PASS':
        f.write('PASS')
        return
    f.write("{x},{y}".format(x=move[0], y=move[1]))

if __name__ == '__main__':
    f = open('input.txt', 'r')
    lines = f.readlines()
    side = int(lines[0].rstrip('\n'))
    previous = ''
    current = ''
    for i in range(1, 6):
        previous += lines[i].rstrip('\n')
    for i in range(6, 11):
        current += lines[i].rstrip('\n')
    go = Board(state=current, previous_state = previous)
    player = MinimaxPlayer()
    player.set_side(side)
    action = player.move(go)
    print_move(action)
    
