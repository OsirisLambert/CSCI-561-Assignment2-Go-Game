from board import Board
from my_player3 import GreedyPlayer, MinimaxPlayer, two_step_check_Player, RandomPlayer

import os

# play one game
def play(board, player1, player2, learn):
    player1.set_side(1)  # black
    player2.set_side(2)  # white
    while not board.game_over():
        player1.move(board)
        player2.move(board)
    if learn:
        player1.learn(board) # black learn
        player2.learn(board) # white learn
    return board.game_result

def battle(board, player1, player2, iter, learn=False, show_result=True):
    p1_stats = [0,0,0] # draw, win, lose
    for i in range(0, iter):
        result = play(board, player1, player2, learn)
        p1_stats[result] += 1 # result return 0 for draw, 1 for black win, 2 for white win, -1 for ongoing
        board.reset()
    p1_stats = [round(x / iter * 100.0, 1) for x in p1_stats] # win rate
    if show_result:
        print('_' * 60)
        print('{:>15}(X) | Wins:{}% Draws:{}% Losses:{}%'.format(player1.__class__.__name__, p1_stats[1], p1_stats[0], p1_stats[2]).center(50))
        print('{:>15}(O) | Wins:{}% Draws:{}% Losses:{}%'.format(player2.__class__.__name__, p1_stats[2], p1_stats[0], p1_stats[1]).center(50))
        print('_' * 60)
        print()
    return p1_stats

if __name__ == "__main__":
    player = MinimaxPlayer()
    #player = GreedyPlayer()
    #player = two_step_check_Player()

    # test: play 1000 games against each opponent
    board = Board(show_board=0)
    print('Playing QLearner against RandomPlayer for 1000 times......')
    q_rand = battle(board, player, two_step_check_Player(), 1)
    rand_q = battle(board, two_step_check_Player(), player, 50)

    # summarize game results
    winning_rate_w_random_player = round(100 - (q_rand[2] + rand_q[1]) / 2, 2)

    print("Summary:")
    print("_" * 60)
    print("QLearner VS  RandomPlayer |  Win/Draw Rate = {}%".format(winning_rate_w_random_player))
    print("_" * 60)
