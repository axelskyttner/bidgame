#!/usr/bin/env python
from dqn_agent import q_agent
from game_engine_rpc import GameEngineRpcClient
import numpy as np
import pika
import uuid
import json
import pprint
#init
fibonacci_rpc = GameEngineRpcClient('molnhatt.se')
agent = q_agent()
pp = pprint.PrettyPrinter(indent=4)

def visualizeGame(trans_list, nameOfWinner):  
    pp.pprint("------------------------------------------")
    pp.pprint("-----------The winner is %s!!-------------" % nameOfWinner) 
    pp.pprint("-----------The transaction list is: ------" )
    pp.pprint( trans_list) 
    pp.pprint("------------------------------------------")
    pp.pprint("------------------------------------------")
    pp.pprint("------------------------------------------")

def keywithmaxval(d):
     """ a) create a list of the dict's keys and values; 
         b) return the key with the max value"""  
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]

class Player():
    def __init__(self, return_value, name):
        self.bid_value = return_value
        self.name = name
    def action(self, state):
        return self.bid_value
        
p1 = Player(1, "p1")
p2 = Player(2, "p2")

players = [p1,p2]
def env_step(input_state, action):
    transaction_list = input_state['transaction_list']
    playername = input_state['name']
    #print(" [x] Requesting fib(30)")
    state = {'transaction-list': transaction_list, 'playername':playername, 'cost':10, 'color':'green'}
    response = json.loads(fibonacci_rpc.call(json.dumps(state)))
    response["reward"] = 1
    return response

endOfGame = False   
transaction_list = []
while not endOfGame:
    #x = np.array([np.zeros(12)])
    #
    #y = np.array([np.zeros(10)])
    
    #pred = agent.predict_next_move(x)
    
    usernames = map(lambda x:x.name, players) 
    values = map(lambda x:x.action({}), players) 
    players_dict = dict(zip (usernames, values))


    winningPlayer = keywithmaxval(players_dict)
    winningBid = players_dict[winningPlayer]

    state = env_step({'transaction_list': transaction_list, 'name':winningPlayer}, 0)

    #print("state", state)
    transaction_list = state["transaction-list"]
    reward = state["reward"]
    winner = state["winner"]
    endOfGame = state["endOfGame"]
    #result = agent.predict_Qf(x)
     
    
     
    #print("bid: ", agent.predict_next_move(x))
    
    #agent.train_model(x,result)

# when game is ended
visualizeGame(transaction_list, winner)
