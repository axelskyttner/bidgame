#!/usr/bin/env python
from BidGame import BidGame
from players import *
from util import is_game_finished, get_color, initialize_player_bids
from util import get_winner
from random import randint    
    
def training_function(transaction_list, players):
    end_of_game = is_game_finished(transaction_list)

    if end_of_game is True:
        winner = get_winner(transaction_list)
    else:
        winner = False

    new_state_to_remember = {
        'transaction_list': transaction_list,
        'color': get_color(),
        'player_bids': initialize_player_bids(players)
    }

    for player in filter(lambda player: player.is_rl(), players):
        if end_of_game and winner == player.name:
            print("player %s is winner, rewarding! " % player.name)
            reward = 1
        elif end_of_game and winner != player.name:
            print("player %s is losing, penalising! " % player.name)
            reward = -1
        else:
            reward = 0
        player.remember(new_state_to_remember, reward, end_of_game)
        player.replay()
        player.target_train()


players = [
           RLPlayer("rl-player"),
           HumanPlayer("p2")
    ]

game = BidGame(players)
player_score = {}
for i in range(10):
    stats = game.run(training_function)
    print("stats", stats)
    winner = stats['winner']
    print("winner is %s" % winner)
    game.visualize(stats)

    if winner not in player_score:
        player_score[winner] = 0

    player_score[winner] += 1


game.save_models("models/2018_03_11")
