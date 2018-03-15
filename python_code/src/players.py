#!/usr/bin/env python
import random
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.optimizers import Adam
# from keras.callbacks import TensorBoard
import numpy as np
from util import convert_state_dict_to_arr, get_total_money_left
from util import get_player_transactions, initialize_player_bids


class HumanPlayer():
    def __init__(self, name):
        self.type = 'default_player'
        self.name = name

    def is_rl(self):
        return False

    def visualize_input(input_state):
        color = input_state['color']
        transaction_list = input_state['transaction_list']
        player_bids = input_state['player_bids']
        print("----------------------------------------------------------")
        print("Now it's time to make a bid on piece of color %s " % color)
        print("The Player bids are  %s " % str(player_bids))
        print("and the previous informatoin is  %s " % str(transaction_list))

    def action(self, input_state):
        if False:
            self.visualize_input(input_state)
        try:
            action = int(input("type your bid: "))
        except ValueError:
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
        transaction_list = input_state['transaction_list']
        player_transactions = get_player_transactions(transaction_list,
                                                      self.name)
        money_left = get_total_money_left(player_transactions)
        return int(np.random.random()*money_left)


class RLPlayer():
    def __init__(self, name, models_path=None):
        self.name = name
        self.batch_size = 10
        self.tau = 0.3
        self.epsilon = 0.3
        self.epsilon_min = 0.1
        self.epsilon_decay = 0.3
        self.learning_rate = 0.01
        self.gamma = 0.5
        if models_path is None:
            print("not loading path")
            self.target_model = self.create_model()
            self.model = self.create_model()
        else:
            self.target_model = load_model("%s/target_model.h5" % models_path)
            self.model = load_model("%s/model.h5" % models_path)
            self.model.summary()
            self.model.compile(loss="mean_squared_error",
                          optimizer=Adam(lr=self.learning_rate))
            print("loaded model")
        self.last_action = 0
        self.last_state = {
            'color': 'Green',
            'current_bid': 0,
            'player_bids': initialize_player_bids([]),
            'transaction_list': []
        }

        self.memory = []

    def is_rl(self):
        return True

    def remember(self, new_state, reward, done):
        action = self.last_action
        state = self.last_state
        state_arr = convert_state_dict_to_arr(state)
        new_state_arr = convert_state_dict_to_arr(new_state)

        self.memory.append([state_arr, action, new_state_arr, reward, done])
        return True

    def create_model(self):
            output_size = 100
            model = Sequential()
            model.add(Dense(24, input_dim=15, activation="relu"))
            model.add(Dense(48, activation="relu"))
            model.add(Dense(24, activation="relu"))
            model.add(Dense(output_size, activation='softmax'))
            model.compile(loss="binary_crossentropy",
                          optimizer=Adam(lr=self.learning_rate))
            model.summary()
            return model

    def replay(self):
        batch_size = self.batch_size
        if len(self.memory) - 1 < batch_size:
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

            # tensorboard_callback = TensorBoard(log_dir='../logs')

            # normalize since we're using sigmoid as last activation function
            normalized_target = target / np.linalg.norm(target[0])
            self.model.fit(state,
                           normalized_target,
                           epochs=10,
                           verbose=0,
                           callbacks=[])

    def target_train(self):
        weights = self.model.get_weights()
        target_weights = self.target_model.get_weights()
        for i in range(len(target_weights)):
            target_weights[i] = weights[i] * self.tau + \
                                target_weights[i] * (1-self.tau)
        self.target_model.set_weights(target_weights)

    def action(self, state):
        state_arr = convert_state_dict_to_arr(state)
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(self.epsilon_min, self.epsilon)

        if np.random.random() < self.epsilon:
            return int(np.random.random()*10 + 0.5)

        state_arr = np.expand_dims(state_arr, axis=0)
        action = np.argmax(self.model.predict(state_arr)[0])

        self.last_action = action
        self.last_state = state

        return action
