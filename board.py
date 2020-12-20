from copy import deepcopy
BOARD_SIZE = 5
ONGOING = -1
DRAW = 0
X_WIN = 1
O_WIN = 2

class Board:
    def __init__(self, state=None, previous_state=None, show_board=False, show_result=False):
        if state is None:
            self.state = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
        else:
            self.state = self.decode_state(state)
        if previous_state is None:
            self.previous_state = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
        else:
            self.previous_state = self.decode_state(previous_state)
        self.game_result = ONGOING
        self.show_board = show_board
        self.show_result = show_result
        self.died_pieces = []
        self.komi = 2.5
        self.n_moves = self.set_n_moves()
        self.max_move = BOARD_SIZE * BOARD_SIZE - 1

    def set_n_moves(self):
        n = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.state[i][j] != 0:
                    n += 1
        return n

    def get_n_moves(self):
        return self.n_moves

    def set_show_board(self, show_board):
        self.show_board = show_board

    def set_previous_state(self,new_state):
        self.previous_state = new_state

    def encode_state(self):
        return ''.join([str(self.state[i][j]) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)])

    def encode_previous_state(self):
        return ''.join([str(self.previous_state[i][j]) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)])

    def decode_state(self, str_state):
        decoded_state = [[0 for x in range(BOARD_SIZE)] for y in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                decoded_state[i][j] = int(str_state[i*BOARD_SIZE+j])
        return decoded_state

    def reset(self):
        self.__init__()

    def is_valid_move(self, i, j, player): 
        if not (0 <= i < BOARD_SIZE):
            return False
        if not (0 <= j < BOARD_SIZE):
            return False
        if self.state[i][j] != 0:
            return False
        test = deepcopy(self)
        test_board = test.state
        test_board[i][j] = player
        if self.has_liberty(test_board, i, j):
            return True
        test_board = self.remove_died_piece(test_board, player)
        if not self.has_liberty(test_board, i, j):
            return False
        else:
            if self.died_pieces and self.compare_board(self.previous_state, test_board):
                return False
        return True

    def has_liberty(self, test_board, i, j):
        state = test_board
        allies = self.detect_allies(state, i,j)
        for member in allies:
            neighbors = self.detect_neighbor(member[0],member[1])
            for piece in neighbors:
                if state[piece[0]][piece[1]] == 0:
                    return True
        return False

    def detect_allies(self, test_board, i, j):
        s = [(i,j)]
        allies = []
        while s:
            piece = s.pop()
            allies.append(piece)
            neighbor_allies = self.detect_neighbor_ally(test_board, piece[0], piece[1])
            for ally in neighbor_allies:
                if ally not in s and ally not in allies:
                    s.append(ally)
        return allies

    def detect_neighbor_ally(self, test_board, i, j):
        state = test_board
        neighbors = self.detect_neighbor(i, j)  
        allies = []
        for piece in neighbors:
            if state[piece[0]][piece[1]] == state[i][j]:
                allies.append(piece)
        return allies

    def detect_neighbor(self, i, j):
        neighbors = []
        if i > 0:
            neighbors.append((i-1, j))
        if i < BOARD_SIZE - 1:
            neighbors.append((i+1, j))
        if j > 0:
            neighbors.append((i, j-1))
        if j < BOARD_SIZE - 1:
            neighbors.append((i, j+1))
        return neighbors

    def remove_died_piece(self,test_board, player):
        state = test_board
        opp = 3 - player
        died_pieces = []
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if state[i][j] == opp:
                    if not self.has_liberty(test_board, i, j):
                        died_pieces.append((i, j))
        if died_pieces:
            for piece in died_pieces:
                state[piece[0]][piece[1]] = 0
        self.died_pieces = died_pieces
        return state

    def compare_board(self, b1, b2):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if b1[i][j] != b2[i][j]:
                    return False
        return True

    def game_over(self, p='NOPASS'):
        if self.n_moves >= self.max_move:
            self.game_result = self._check_winner()
            return True
        if p == "PASS" and self.compare_board(self.previous_state, self.state):
            self.game_result = self._check_winner()
            return True
        return False

    def _check_winner(self):   
        black = self.score(1)
        white = self.score(2)
        if black > white + self.komi:
            return X_WIN
        elif black < white + self.komi:
            return O_WIN
        else:
            return DRAW

    def score(self, player):
        board = self.state
        count = 0
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i][j] == player:
                    count += 1
        return count

    def move(self, i, j, player, p='NOPASS'):
        if self.game_over(p):
            self.game_result = self._check_winner()
        if self.is_valid_move(i,j,player):
            self.n_moves += 1
            self.set_previous_state(deepcopy(self.state))
            self.state[i][j] = player  
            self.state = self.remove_died_piece(self.state, player)
        if self.show_board:
            p = 'X' if player == 1 else 'O'
            print('player {} moved: {}, {}'.format(p,i,j))
            self.print_board()
        if self.show_result:
            self.game_result_report()

    def print_board(self):
        state = self.encode_state() 
        state = state.replace('0', ' ').replace('1', 'X').replace('2', 'O')
        o = ''
        print('-'*7)
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                o += state[i*BOARD_SIZE+j]
            print('|' + o + '|')
            o = ''
        print('-' * 7)

    def game_result_report(self):
        if self.game_result is ONGOING:
            return
        print ('=' * 30)
        if self.game_result is DRAW:
            print ('Game Over : Draw'.center(30))
        elif self.game_result is X_WIN:
            print ('Game Over : Winner BLACK X'.center(30))
        elif self.game_result is O_WIN:
            print ('Game Over : Winner WHITE O'.center(30))
        print ('=' * 30)

    def cal_liberties(self, side):
        opp = 3 - side
        score_list = [0]*3
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.state[i][j] != 0:
                    neighbors = self.detect_neighbor(i,j)
                    for neighbor in neighbors:
                        if self.state[neighbor[0]][neighbor[1]] == 0:
                            score_list[self.state[i][j]] += 1
        return score_list[side] - score_list[opp]

    def get_died_pieces(self):
        return self.died_pieces



if __name__ == '__main__':
    state = Board(state='0000000000012011202001200',previous_state='0000000000012011012001200')
    state.move(3,2,1)
    s = state.cal_num_on_edge(1)
    state.print_board()
    print(s)

