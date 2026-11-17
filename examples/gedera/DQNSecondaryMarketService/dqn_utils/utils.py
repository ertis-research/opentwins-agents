import keras
from keras import layers
import numpy as np
import tensorflow as tf




def create_q_model(NUM_ACTIONS):
    inputs = layers.Input(shape=(127,))

    layer1 = layers.Dense(128, input_shape=(127,), activation='relu')(inputs)
    layer2 = layers.Dense(256, activation='relu')(layer1)
    layer3 = layers.Dense(512, activation='relu')(layer2)
    
    layer4 = layers.Dense(512, activation="relu")(layer3)
    layer4_1 = layers.Dense(256, activation='relu')(layer4)
    layer4_2 = layers.Dense(128, activation='relu')(layer4_1)
    advantage = layers.Dense(NUM_ACTIONS, activation="linear")(layer4_2)

    layer5 = layers.Dense(512, activation="relu")(layer3)
    layer5_1 = layers.Dense(256, activation='relu')(layer5)
    layer5_2 = layers.Dense(128, activation='relu')(layer5_1)
    value = layers.Dense(1, activation="linear")(layer5_2)

    output = value + advantage - tf.reduce_mean(advantage)
    
    
    return keras.Model(inputs=inputs, outputs=output)


def create_q_model_second_model(num_actions):
    model = keras.Sequential()
    model.add(layers.Dense(128, input_shape=(127,), activation='relu'))
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(num_actions, activation='linear'))
    #model.compile(loss='mse', optimizer='adam', metrics=['mae'])
    return model





def create_q_model_first_model(num_actions):
    model = keras.Sequential()
    model.add(layers.Dense(128, input_shape=(127,), activation='relu'))
    model.add(layers.Dense(256, activation='relu'))
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(num_actions, activation='linear'))
    #model.compile(loss='mse', optimizer='adam', metrics=['mae'])
    return model