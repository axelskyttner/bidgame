#!/usr/bin/env python
import random
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
import numpy as np


def count_number_of_colors(player_transactions):
    nr_colors = {
        'RED': 0,
        'BLUE': 0,
        'GREEN': 0
    }
    for player_transaction in player_transactions:

        nr_colors[player_transaction["color"].upper()] += 1

    return nr_colors


def get_total_money_left(player_transactions):
    total_amount = 100
    cost_list = [transaction['cost'] for transaction in player_transactions]
    money_spent = sum(cost_list)
    return total_amount - money_spent


def get_name(transaction):
    return transaction['name']


# fix: this is broken
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
    def __init__(self, name):
        self.name = name
        self.batch_size = 1
        self.tau = 0.3
        self.epsilon = 0.3
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.3
        self.learning_rate = 0.5
        self.gamma = 0.5
        self.target_model = self.create_model()
        self.model = self.create_model()
        self.last_action = 0
        self.last_state = {
            'color': 'Green',
            'current_bid': 0,
            'transaction_list': []
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

    # def how should this be created?
    def convert_state_dict_to_arr(self, state_dict):

        # following rgb convention
        current_color_index_dictionary = {
            'RED': 0,
            'GREEN': 1,
            'BLUE': 2
        }

        current_color = state_dict['color'].upper()
        current_color_index = current_color_index_dictionary[current_color]

        transaction_list = state_dict['transaction_list']

        player_names = list(set(map(get_name, transaction_list)))

        players_information = {}
        for player_name in player_names:
            player_information = {}
            player_transactions = [transaction for transaction in transaction_list if transaction['name'] == player_name]
            nr_colors = count_number_of_colors(player_transactions)
            money_left = get_total_money_left(player_transactions)
            player_information['colors'] = nr_colors
            player_information['money_left'] = money_left
            players_information[player_name] = player_information

        nr_players = 2
        nr_colors = 3
        state_arr = np.zeros((nr_players+1, nr_colors+2))

        # add all the player specific information to array
        for player_index, player_name in enumerate(player_names):
            color_info = players_information[player_name]['colors']

            for color_index, color_value in enumerate(color_info.values()):
                state_arr[player_index][color_index] = color_value

            money_left_index = -1
            state_arr[player_index][money_left_index] = players_information[player_name]['money_left']

        # add the misc layer
        state_arr[-1, current_color_index] = 1

        return state_arr.flatten()

    def create_model(self):
            output_size = 10
            model = Sequential()
            state_shape = 15
            model.add(Dense(24, input_dim=state_shape, activation="relu"))
            model.add(Dense(48, activation="relu"))
            model.add(Dense(24, activation="relu"))
            model.add(Dense(output_size))
            model.compile(loss="mean_squared_error",
                optimizer=Adam(lr=self.learning_rate))
            return model


    def replay(self):
        batch_size = self.batch_size
        if len(self.memory) -1  < batch_size:
            return
    
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
            target_weights[i] = weights[i] * self.tau + target_weights[i] * (1-self.tau)
        self.target_model.set_weights(target_weights)

    def action(self, state):
        state_arr = self.convert_state_dict_to_arr(state)
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)

        if np.random.random() < self.epsilon:
            return int(np.random.random()*10 + 0.5)

        state_arr = np.expand_dims(state_arr, axis=0)
        action = np.argmax(self.model.predict(state_arr)[0])

        self.last_action = action
        self.last_state = state
        print("action of RL-player: %i" % action)
        print("during state %s" % str(state_arr))
        return action
