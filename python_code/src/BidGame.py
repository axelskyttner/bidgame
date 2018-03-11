#!/usr/bin/env python
from game_engine_rpc import GameEngineRpcClient
from players import RLPlayer
from players import RandomPlayer
import json
import pprint
import numpy
from collections import Counter

from util import get_player_transactions, get_total_money_left


def keywithmaxval(d):
    """ a) create a list of the dict's keys and values;
        b) return the key with the max value"""
    v = list(d.values())
    k = list(d.keys())
    return k[v.index(max(v))]


def get_color():
    colorList = ["RED", "BLUE", "GREEN"]
    return numpy.random.choice(colorList)


def player_can_afford_it(transaction_list, player_name, bid):
    player_transactions = get_player_transactions(transaction_list,
                                                  player_name)
    money_left = get_total_money_left(player_transactions)
    if money_left >= bid:
        return True
    else:
        return False


def initialize_player_bids(players):
    player_bids = {}
    for player in players:
        player_bids[player.name] = 0

    return player_bids


def get_players(transaction_list):
    return list(set(map(lambda x: x['name'], transaction_list)))


def get_player_score(transaction_list, player_name):
    most_common_color = get_most_common_color(transaction_list, 1)
    snd_most_common_color = get_most_common_color(transaction_list, 2)
    player_transactions = get_player_transactions(transaction_list,
                                                  player_name)
    player_colors = [trans['color'] for trans in player_transactions]

    top_scores = [3 for color in player_colors if color == most_common_color]
    snd_top_scores = [1 for color in player_colors if color == snd_most_common_color]
    return sum(top_scores) + sum(snd_top_scores)


def get_winner(transaction_list):
    players = get_players(transaction_list)
    player_scores = {}
    for player in players:
        player_score = get_player_score(transaction_list, player)
        player_scores['player'] = player_score

    return keywithmaxval(player_scores)


def get_most_common_color(transaction_list, n=1):
    color_list = [trans['color'] for trans in transaction_list]
    counted_list = Counter(color_list).most_common(n)

    # we do not want to ask for snd most common if only one color exists
    if len(counted_list) < n:
        return ""

    nth_most_common_color, nr_of_nth_color = counted_list[n-1]
    return nth_most_common_color


def is_game_finished(transaction_list):
    color_list = [trans['color'] for trans in transaction_list]
    most_common_color, nr_of_one_color = Counter(color_list).most_common(1)[0]
    return nr_of_one_color > 2


class BidGame():
    def __init__(self, host='localhost'):
        self.engine_rpc = GameEngineRpcClient(host)
        self.pp = pprint.PrettyPrinter(indent=4)

        self.players = [
                   RLPlayer("rl-player"),
                   # DefaultPlayer("p2", 8)
                   RandomPlayer("p2")
                   # HumanPlayer("human")
            ]

    def visualize(self, state):
        transaction_list = state['transaction_list']
        winner = state['winner']
        pp = self.pp
        if(winner is False):
            pp.pprint("Oops, no winner, is there player's connected?")
            pp.pprint("transactionlist: %s" % str(transaction_list))
            return False

        pp.pprint("------------------------------------------")
        pp.pprint("-----------The winner is %s!!-------------" % winner)
        pp.pprint("-----------The transaction list is: ------")
        pp.pprint(transaction_list)
        pp.pprint("------------------------------------------")
        pp.pprint("------------------------------------------")
        pp.pprint("------------------------------------------")

    def env_step(self, input_state):
        transaction_list = input_state['transaction_list']
        playername = input_state['name']
        bid = input_state['cost']
        color = input_state['color']
        transaction_list.append({
            'cost': int(bid),
            'color': color,
            'name': playername

            })

        end_of_game = is_game_finished(transaction_list)
        if end_of_game is True:
            winner = get_winner(transaction_list)
        else:
            winner = False

        state = {
                'transaction_list': transaction_list,
                'winner': winner,
                'endOfGame': end_of_game
                }
        return state

    def play_round(self, players, color, transaction_list):

        # initialise bids
        player_bids = initialize_player_bids(players)
        for player in players:
            player_name = player.name
            current_state = {
                'color': color,
                'transaction_list': transaction_list,
                'player_bids': player_bids
               }

            player_action = player.action(current_state)
            payment_ok = player_can_afford_it(transaction_list,
                                              player_name,
                                              player_action)
            if payment_ok:
                player_bids[player_name] = player_action
            else:
                player_bids[player_name] = 0

        winningPlayer = keywithmaxval(player_bids)
        winningBid = player_bids[winningPlayer]

        playername = winningPlayer
        bid = winningBid
        transaction_list.append({
            'cost': int(bid),
            'color': color,
            'name': playername

            })

        print(transaction_list)
        return transaction_list


    def run(self):

        transaction_list = []
        players = self.players
        rlPlayer = players[0]
        end_of_game = False if len(players) > 0 else True
        while not end_of_game:
            color = get_color()
            transaction_list = self.play_round(players, color, transaction_list)

            end_of_game = is_game_finished(transaction_list)
            if end_of_game is True:
                winner = get_winner(transaction_list)
            else:
                winner = False

            # this is only for RL
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
                    reward = -1
                else:
                    reward = 0
                player.remember(new_state_to_remember, reward, end_of_game)
                rlPlayer.replay()
                rlPlayer.target_train()

        print("end of game")
        winner_name = winner

        return {'transaction_list': transaction_list, 'winner': winner_name}
