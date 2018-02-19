from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import TensorBoard
import numpy as np
from time import time

class q_agent:
    def __init__(self):
        self.x = 1
        self.y = 2
        self.model = self.create_model()
        self.epochs = 100
    def create_model(self):
        model = Sequential()  
        model.add(Dense(5, input_shape = (12,)))
        model.add(Dense(10, activation='linear'))
        model.compile(optimizer = 'sgd', loss='mean_squared_error')
        return model
    def get_model(self):
        return self.model
    
    def train_model(self, training_data, y, callbacks = []):
        model = self.model

        model.fit(training_data,y, epochs=self.epochs, callbacks = callbacks)

        # fix: remove this return
        return 2

    def predict_Qf(self,bid_information):
        model = self.get_model()
        result = model.predict( bid_information )
        return result

    #this function is the one that should be used as callback
    def predict_next_move(self, bid_information):
        model = self.get_model()
        result = model.predict( bid_information )
        highest_values = np.argmax(result, axis=1)
        cost_values = list(map(lambda x : x*10,highest_values))
        return cost_values[0] 
