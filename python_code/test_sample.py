from players import RLPlayer, DefaultPlayer
from BidGame import BidGame
import numpy as np

def get_state():
    return {
        'color':'Green',
        'current_bid': 10,
        'transaction_list':[]

    } 

def test_RL_remember():
    player = RLPlayer("axel")
    state=  get_state()
    newState =  get_state()
    reward = 1
    done = False
    action = 8 
 
    player.remember(state, reward, done)
    player.remember(state, reward, done)
    assert len(player.memory) == 2



def test_RL_create_model():
    player = RLPlayer("p1")
    model = player.create_model()


def test_RL_replay():
    player = RLPlayer("p1")
    state=  get_state()
    newState =  get_state()
    reward = 1
    done = False
    action = 4
    player.remember(state, reward, done)
    player.remember(state, reward, done)
    player.replay()

def test_RL_action():
    player = RLPlayer("axel")
    state = get_state()
    player.action(state)
    assert 2==2

def test_RL_action():
    player = RLPlayer("axel")
    state = get_state()
    player.action(state)
    assert player.last_state['transaction_list'] == []
    assert player.last_action >= 0

def test_RL_target_train():
    player = RLPlayer("axel")
    state = np.zeros((1,12))
    player.target_train()
    assert 2==2

def test_RK_state_convert():
    state= {
        'color':'Green',
        'current_bid':10,
        'transaction_list':[]
    } 
    p = RLPlayer("p1")
    arr = p.convert_state_dict_to_arr(state)
    assert arr.shape == (15,)

def test_default_player_init():
    p1 = DefaultPlayer('name', 10)
    assert p1.type == 'default_player'


def test_default_player_action():
    p1 = DefaultPlayer('name', 10)
    assert p1.action({}) ==10


def test_play_round_no_players():
    game = BidGame()
    new_state = game.play_round([], 'green', [])
    assert new_state == []

def test_play_round_one_user():
    player = DefaultPlayer("p1", 20)
    game = BidGame()
    new_state = game.play_round([player], 'green', [])
    print("new_state", new_state)
    new_trans_list = new_state['transaction-list']



def test_convert_state_dict_to_arr_1():
    player = RLPlayer("p1")
    state = {
        'transaction_list':[],
        'color':'Green',
        'current_bid':1
    }
    arr = player.convert_state_dict_to_arr(state)
    assert arr[9]  == 1


def test_convert_state_dict_to_arr_2():
    player = RLPlayer("p1")
    state = {
        'transaction_list':[
            {
            'color': 'RED',
            'cost': 10,
            'name': 'p1'
            }
                  
        ],
        'color':'Green',
        'current_bid':1
    }
    arr = player.convert_state_dict_to_arr(state)
    assert arr[0]  == 1
