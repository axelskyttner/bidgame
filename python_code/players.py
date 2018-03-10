#!/usr/bin/env python
import uuid
import numpy
import random
from keras.models import Sequential 
from keras.layers import  Dense
from keras.optimizers import  Adam
import numpy as np

class RpcPlayer():
    def __init__(self, name, queue_name):
        self.javascript_rpc = JavascriptRpcClient(queue_name, 'molnhatt.se')
        self.name = name
    
    def is_rl(self):
        return False
    def action(self, state):
        color = state['color']
        bid = state['current_bid']
        transaction_list = state['transaction_list']
        json_info = json.dumps({'color':color, 'bid':bid, 'transaction-list':[]})
        bidvalue = self.javascript_rpc.call(json_info)
        
        return bidvalue
   

class HumanPlayer():
    def __init__(self, name):
        self.type = 'default_player'
        self.name = name
    
    def is_rl(self):
        return False

    def action(self, input_state):
        try:
            action =  int(input("type your bid"))
        except:
            action = 0
        return action

class DefaultPlayer():
    def __init__(self, name, bid_value):
        self.type = 'default_player'
        self.name = name
        self.default_bid_value = bid_value
    
    def is_rl(self):
        return False
    def action(self, input_state):

        return self.default_bid_value


class RandomPlayer():
    def __init__(self, name):
        self.type = 'random_player'
        self.name = name
    
    def is_rl(self):
        return False

    def action(self, input_state):
        return int(np.random.random()*10) 

class RLPlayer():
    def __init__(self, name ):
        self.name = name
        self.batch_size = 1 
        self.tau = 0.3
        self.epsilon = 0.3
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.3
        self.learning_rate = 0.5 #??    
        self.gamma = 0.5
        self.target_model = self.create_model()
        self.model = self.create_model()
        self.last_action = 0
        self.last_state = {
            'color':'Green',
            'current_bid':0,
            'transaction_list':[] 
        }

        self.memory = []

    def is_rl(self):
        return True

    def remember(self, new_state, reward, done):
        action = self.last_action
        state = self.last_state 
        state_arr = self.convert_state_dict_to_arr(state)
        new_state_arr = self.convert_state_dict_to_arr(new_state)
        
        self.memory.append([state_arr, action, new_state_arr, reward, done]) 
        return True
   
    #def how should this be created? 
    def convert_state_dict_to_arr(self, state_dict):

        # this is the index in the arrya for colors. 
        # fix: maybe exists better solution?
        current_color_index_dictionary = {
            'GREEN':10,
            'RED':11,
            'BLUE': 12
        }
        color_index = current_color_index_dictionary[state_dict['color'].upper()]
        
        transaction_list = state_dict['transaction_list']

        player_names = list(set(map(lambda transaction: transaction['name'], transaction_list)))

        color_information = []
        for player_name in player_names:

            player_transactions = list(filter(lambda transaction: transaction['name'] == player_name, transaction_list))

            nr_colors = {
                'RED': 0,
                'BLUE': 0,
                'GREEN': 0
            }
            for player_transaction in player_transactions:
                
                nr_colors[player_transaction["color"].upper()] += 1

            color_information.append(nr_colors)

        current_bid = state_dict['current_bid']
        
        state_arr = np.zeros(15)  
        state_arr[9] = current_bid
        state_arr[color_index] = 1
        for color_info,start_index in zip(color_information,[0,5]):
         
            state_arr[start_index] = color_info['RED']
            state_arr[start_index + 1] = color_info['GREEN']
            state_arr[start_index + 2] = color_info['BLUE']

        return state_arr 
        
    
    
    def create_model(self):
            output_size = 10
            model   = Sequential()
            state_shape  = 15
            model.add(Dense(24, input_dim=state_shape, activation="relu"))
            model.add(Dense(48, activation="relu"))
            model.add(Dense(24, activation="relu"))
            model.add(Dense(10))
            model.compile(loss="mean_squared_error",
                optimizer=Adam(lr=self.learning_rate))
            return model


    def replay(self):
        batch_size = self.batch_size
        if len(self.memory) -1  < batch_size: 
            return
    
        #slice all but last, since last is for next sample
        samples = random.sample(self.memory, batch_size)
        for sample in samples:
            state, action, new_state, reward, done = sample
            state = np.expand_dims(state, axis=0)
            target = self.target_model.predict(state)

            if done:
                target[0][action] = reward
            else:
                new_state = np.expand_dims(new_state, axis=0)
                Q_future = max(self.target_model.predict(new_state)[0])
                target[0][action] = reward + Q_future * self.gamma

            self.model.fit(state, target, epochs=100, verbose=0)

    
    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1 - self.tau)
        self.target_model.set_weights(target_weights)

    def action(self, state):
        state_arr = self.convert_state_dict_to_arr(state)
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)
        if np.random.random() < self.epsilon:
            #fix is this correct rounded?
            return int(np.random.random()*10)

        state_arr = np.expand_dims(state_arr, axis=0)
        action =  np.argmax(self.model.predict(state_arr)[0])


        self.last_action = action 
        self.last_state = state
        print("action of RL-player: %i" % action)
        print("during state %s" % str(state_arr))
        return action

