#!/usr/bin/env python
import pprint
from util import is_game_finished, get_winner, initialize_player_bids
from util import player_can_afford_it, keywithmaxval, get_color


class BidGame():
    def __init__(self, players, host='localhost'):
        self.pp = pprint.PrettyPrinter(indent=4)
        self.players = players

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

    def play_round(self, players, color, transaction_list):

        player_bids = initialize_player_bids(players)
        for player in players:
            player_name = player.name
            current_state = {
                'color': color,
                'transaction_list': transaction_list,
                'player_bids': player_bids
               }

            player_action = player.action(current_state)
            payment_is_ok = player_can_afford_it(transaction_list,
                                                 player_name,
                                                 player_action)
            if payment_is_ok:
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

        return transaction_list

    def run(self, training_function=None):

        transaction_list = []
        players = self.players
        end_of_game = False if len(players) > 0 else True
        while not end_of_game:
            color = get_color()
            transaction_list = self.play_round(players,
                                               color,
                                               transaction_list)

            end_of_game = is_game_finished(transaction_list)
            if end_of_game is True:
                winner = get_winner(transaction_list)
            else:
                winner = False

            if training_function is not None:
                training_function(transaction_list, players)

        return {'transaction_list': transaction_list, 'winner': winner}

    def save_models(self, folder_path):
        players = self.players
        for player in filter(lambda player: player.is_rl(), players):
            player.model.save("%s/model.h5" % folder_path)
            player.target_model.save("%s/target_model.h5" % folder_path)
