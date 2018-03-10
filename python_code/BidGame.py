#!/usr/bin/env python
from game_engine_rpc import GameEngineRpcClient
from players import RpcPlayer, RLPlayer, DefaultPlayer, RandomPlayer, HumanPlayer
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




class BidGame():
    def __init__(self, host = 'localhost'):
        self.engine_rpc = GameEngineRpcClient(host)
        self.pp = pprint.PrettyPrinter(indent=4)
        
        self.players = [ 
                   RLPlayer("rl-player"),
                   #DefaultPlayer("p2", 8)
                   RandomPlayer("p2")
                   #HumanPlayer("human")
            ]
    
    def visualize(self, state):
        transaction_list = state['transaction_list'] 
        winner = state['winner'] 
        pp = self.pp
        if(winner == False):
            pp.pprint("Oops, no winner, is there player's connected?")
            pp.pprint("transactionlist: %s" % str(transaction_list))
            return False

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
                'cost':int(bid), 
                'color':color
                }
        json_to_send = json.dumps(state)
        response_json = engine_rpc.call(json.dumps(state))
        response = json.loads(response_json)
        return response

    def play_round(self,players, color, transaction_list):
    
        # need players for playing a round
        if len(players) == 0:
            return []
    
        usernames = map(lambda x:x.name, players) 
    
        list_with_bids = []
        highest_score = 0
        state_to_rember = {}
        action_to_remember = False
        state_to_remember = False
        for player in players:
    
            if(len(list_with_bids) > 0):
                highest_score = max(list_with_bids) 
    
            current_state = {   
                'color':color,  
                'transaction_list': transaction_list ,
                'current_bid': highest_score 
               }
            player_action = player.action(current_state) 
            list_with_bids.append(player_action)
    
        players_dict = dict(zip (usernames, list_with_bids))
        winningPlayer = keywithmaxval(players_dict)
        winningBid = players_dict[winningPlayer]
    
        new_state = self.env_step({
                        'transaction_list': transaction_list, 
                        'name':winningPlayer, 
                        'cost': winningBid, 
                        'color':color
                        })

        transaction_list = new_state["transaction-list"]
        endOfGame = new_state["endOfGame"]

        new_state_to_remember = {

            'transaction_list':transaction_list,
            'color':get_color(),
            'current_bid':0
        } 

        for player in players:
            if player.is_rl():
                if endOfGame and new_state['winner'] == player.name:
                    print("player %s is winner, rewarding! " % player.name)
                    reward = 1
                elif endOfGame and new_state['winner'] != player.name:
                    reward = -1
                else :
                    reward = 0
                player.remember(new_state_to_remember, reward, endOfGame ) 

        return new_state

    def run(self):        

        transaction_list = []
        players = self.players
        rlPlayer = players[0]    
        winner = False 
        endOfGame = False if len(players) > 0 else True   
        while not endOfGame:
            color = get_color()      
            new_state = self.play_round(players, color, transaction_list)
            endOfGame = new_state['endOfGame']
            transaction_list = new_state['transaction-list']

        winner_name = new_state["winner"]

        print("end of game")    

        #learn
        for player in players:
            if player.is_rl():
                if(winner == "rl-player"):
                    reward = 1
                else:
                    reward = -1
                rlPlayer.replay()
                rlPlayer.target_train()
        
        return {'transaction_list':transaction_list, 'winner':winner_name} 
        
        
        
        
