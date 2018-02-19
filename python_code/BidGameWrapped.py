#!/usr/bin/env python
import json
import pprint
import numpy


def keywithmaxval(d):
     """ a) create a list of the dict's keys and values;
         b) return the key with the max value"""
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]



def get_color():
    colorList = ["RED", "BLUE", "GREEN"]
    return numpy.random.choice(colorList)


def play_round(players, color, transaction_list):
    usernames = map(lambda x:x.name, players)

    values = []
    highest_score = 0
    for player in players:
        if(len(values) > 0):
            highest_score = max(values)
        values.append(player.action(
                                    {   'color':color,
                                       'transaction_list': transaction_list ,
                                       'current_bid': highest_score
                                    }))

    players_dict = dict(zip (usernames, values))
    winningPlayer = keywithmaxval(players_dict)
    winningBid = players_dict[winningPlayer]

    return {"name": winningPlayer, 'bid': winningBid}


class BidGame():
    def __init__(self):
        #fix: rename and add javascript client
        self.engine_rpc = FibonacciRpcClient()
        self.pp = pprint.PrettyPrinter(indent=4)

        self.players = [ Player("p1",'player-1-queue' ),
                    Player("p2",'player-2-queue' )
            ]

    def visualize(self, state):
        transaction_list = state['transaction_list']
        winner = state['winner']
        pp = self.pp

        pp.pprint("------------------------------------------")
        pp.pprint("-----------The winner is %s!!-------------" % winner)
        pp.pprint("-----------The transaction list is: ------" )
        pp.pprint( transaction_list)
        pp.pprint("------------------------------------------")
        pp.pprint("------------------------------------------")
        pp.pprint("------------------------------------------")


    def env_step(self, input_state):
        engine_rpc  = self.engine_rpc
        transaction_list = input_state['transaction_list']
        playername = input_state['name']
        bid = input_state['cost']
        color = input_state['color']

        state = {
                'transaction-list': transaction_list,
                'playername':playername,
                'cost':bid,
                'color':color
                }

        response = json.loads(engine_rpc.call(json.dumps(state)))
        return response


    def run(self):

        endOfGame = False
        transaction_list = []
        players = self.players


        while not endOfGame:
            color = get_color()
            winning_bid = play_round(players, color, transaction_list)
            winningPlayer= winning_bid['name']
            bid= winning_bid['bid']

            state = self.env_step({
                    'transaction_list': transaction_list,
                    'name':winningPlayer,
                    'cost': bid,
                    'color':color
                    })

            transaction_list = state["transaction-list"]
            winner = state["winner"]
            endOfGame = state["endOfGame"]
            print("end of game?")

        print("end of game")
        return {'transaction_list':transaction_list, 'winner':winner}




