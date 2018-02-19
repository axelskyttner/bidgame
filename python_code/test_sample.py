from dqn_agent import q_agent
from BidGame import play_round
from players import Player
import numpy as np
from keras.callbacks import TensorBoard
from time import time

# content of test_sample.py
def func(x):
    return x + 1

def test_answer():
    agent = q_agent()
    assert agent.x == 1


def test_model():
    agent = q_agent()
    model= agent.create_model()
    #fix: what is the length of inputs?
    assert len(model.inputs) == 1

def test_train_model():
    agent = q_agent()
    state = []
    training_data = np.array([
            np.zeros(12),
            np.zeros(12),
            np.zeros(12)
        ])

    y1 = np.zeros(10) 
    y2 = np.zeros(10) 
    y3 = np.zeros(10) 
    y1[2] = 1
    y2[2] = 1
    y3[2] = 1
    y = np.array([
        y1,
        y2,
        y3
    ])

    tensorboard = TensorBoard(log_dir="logs/{}".format(time()))
    agent.train_model(training_data, y, [tensorboard])

    assert 2 == 2

def test_predict_next_move():
    agent = q_agent()
    training_data = np.array([
            np.zeros(12),
            np.zeros(12),
            np.zeros(12)
        ])


    y1 = np.zeros(10) 
    y2 = np.zeros(10) 
    y3 = np.zeros(10) 
    y1[2] = 1
    y2[2] = 1
    y3[2] = 1
    y = np.array([
        y1,
        y2,
        y3
    ])
    agent.train_model(training_data, y)
    x = np.array([
            np.zeros(12)
         ] )
    eval_results = agent.predict_next_move(x)
    print("eval_results", eval_results)
    assert (eval_results % 10 == 0) and (eval_results < 100) 

def test_player_interface():
    p1 = Player("axel", 'player-1-queue')
    bid = p1.action({
            'transaction_list':[],
            'color':"green",
             'current_bid': 30
        })
    assert(bid > 0)
                        

def test_run_bid_round():
   p1 = Player("test1", 'player-1-queue')
   p2 = Player("test2",'player-1-queue')
   winning_player_dict = play_round([p1,p2], "green", [])
   assert(winning_player_dict['name'] == "test1") 
