
from datetime import datetime
# TENSORFLOW AND KERAS THINGS
import os
os.environ["KERAS_BACKEND"] = "tensorflow"
import keras
from keras import layers
import numpy as np
import pandas as pd
import tensorflow as tf
from dqn_utils.utils import create_q_model

# ENV THINGS
from adabyron_environment.mercadoSecundario_v2 import MercadoSecundario
from adabyron_environment.agents.storageBattery_mercado_secundario import StorageBatteryMS
import matplotlib.pyplot as plt     

SEED = 42
GAMMA = 0.99 # Discount factor for past rewards
EPSILON = 1.0 # Epsilon greedy parameter
EPSILON_MIN = 0.1 # Minimum epsilon greedy parameter
EPSILON_MAX = 1.0 # Decay rate for epsilon greedy parameter

epsilon_interval = (
    EPSILON_MAX - EPSILON_MIN
)  # Rate at which to reduce chance of random action being taken

BATCH_SIZE = 32 # Size of batch taken from replay buffer
MAX_STEPS_PER_EPISODE = 100000
MAX_EPISODES = 100000^2 # Number of episodes to run



#################################################
######### ENVIRONMENT INITIALIZATION ############
#################################################

bandaSecundaria = pd.read_csv('test_data/bandaSecundaria.csv', sep=';')
bandaSecundaria['value'] = bandaSecundaria['value']
bandaSecundaria = list(bandaSecundaria['value'])

regulacionSubir = pd.read_csv('test_data/regulacionSubir.csv', sep=';')
regulacionSubir['value'] = regulacionSubir['value']
regulacionSubir = list(regulacionSubir['value'])

regulacionBajar = pd.read_csv('test_data/regulacionBajar.csv', sep=';')
regulacionBajar['value'] = regulacionBajar['value']
regulacionBajar = list(regulacionBajar['value'])

highPercentage  = [0.00, 57.23, 99.90, 79.97, 41.21, 9.35, 0.00,  0.00, 41.78, 24.21, 49.70, 33.65, 9.66, 1.97, 25.84, 83.23, 0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00,  0.00]
lowPercentage   = [9.03, 0.00,  0.00,  0.00,  0.00,  0.00, 60.97, 0.96, 0.00,  0.00,  0.00,  0.00,  0.00, 0.00, 0.00,  0.00,  65.25, 24.78, 61.28, 65.14, 72.64, 99.30, 99.36, 69.52]

########## REDUCE DAY LENGTH FOR TESTING PURPOSES
bandaSecundaria = np.array(bandaSecundaria).reshape(-1,3).mean(axis=1)
regulacionSubir = np.array(regulacionSubir).reshape(-1,3).mean(axis=1)
regulacionBajar = np.array(regulacionBajar).reshape(-1,3).mean(axis=1)
highPercentage = np.array(highPercentage).reshape(-1,3).mean(axis=1)
lowPercentage = np.array(lowPercentage).reshape(-1,3).mean(axis=1)


energy_fixed_input = np.array([bandaSecundaria, regulacionSubir, highPercentage, regulacionBajar, highPercentage]).flatten()

battery = StorageBatteryMS("B1",capacity= 36, original_soc = 23)
battery_capacity = battery.capacity
mercadoSecundario = MercadoSecundario(preservedEnergy=0.50, 
                                      priceCurve= bandaSecundaria, 
                                      highCurve= regulacionSubir, 
                                      lowCurve= regulacionBajar,
                                      highPercentage= highPercentage,
                                      lowPercentage= lowPercentage,
                                      battery= battery)

total_actions = battery.get_action_space()

first_state = mercadoSecundario.reset()




#################################################
######### DQN MODEL INITIALIZATION ##############
#################################################

model = create_q_model(total_actions)
model_target = create_q_model(total_actions)

optimizer = keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)

# Experience replay buffers
action_history = []
state_history = []
state_next_history = []
rewards_history = []
done_history = []
episode_reward_history = []
running_reward = 0
episode_count = 0
frame_count = 0

# Number of frames to take random action and observe output
epsilon_random_frames = 50000
# Number of frames for exploration
epsilon_greedy_frames = 1000000.0
# Maximum replay length
max_memory_length = 100000

# Train the model after 4 actions
update_after_actions = 4
# How often to update the target network
update_target_network = 10000
# Using huber loss for stability
loss_function = keras.losses.Huber()

save_model_path = "models/"



def dibujaGraficaQ():
    print("Dibujo graficas")
    
    test_battery = StorageBatteryMS("B1",capacity= 36, original_soc = 23)
    test_mercadoSecundario = MercadoSecundario(preservedEnergy=0.50, 
                                        priceCurve= bandaSecundaria, 
                                        highCurve= regulacionSubir, 
                                        lowCurve= regulacionBajar,
                                        highPercentage= highPercentage,
                                        lowPercentage= lowPercentage,
                                        battery= test_battery)
    
    proto_testing_state = test_mercadoSecundario.reset()
    
    testing_qvalues = []
    while True:
        testing_state = [proto_testing_state.day_step, 
                         proto_testing_state.cumulative_consumption, 
                         proto_testing_state.cumulative_price, 
                         proto_testing_state.agents_info['B1']['soc'], 
                         battery_capacity, 
                         proto_testing_state.agents_info['B1']['chargeHistory'], 
                         proto_testing_state.agents_info['B1']['dischargeHistory']] + energy_fixed_input.tolist()
        
        testing_state_tensor = tf.convert_to_tensor([testing_state])
        testing_action_probs = model(testing_state_tensor, training=False)
        testing_qvalues.append(tf.reduce_max(testing_action_probs).numpy())
        
        proto_testing_state_next, _, test_done = test_mercadoSecundario.step_dqn(proto_testing_state, action)
        proto_testing_state = proto_testing_state_next
        
        if test_done: break  
        
        
        
    media = tf.reduce_mean(testing_qvalues).numpy() 
    
    plt.plot(media)
    plt.savefig("images/DQN/qvalues_{}.jpg".format(datetime.now().strftime('%H_%M_%S')))
    plt.close()

#################################################
######### DQN TRAINING ##########################
#################################################
while True:
    # Get first state
    proto_state = mercadoSecundario.reset()
    state = [proto_state.day_step, proto_state.cumulative_consumption, proto_state.cumulative_price, proto_state.agents_info['B1']['soc'], battery_capacity, proto_state.agents_info['B1']['chargeHistory'], proto_state.agents_info['B1']['dischargeHistory']] + energy_fixed_input.tolist()
    episode_reward = 0
    
    for timestep in range(1, MAX_STEPS_PER_EPISODE):
        frame_count += 1
        
        # Use epsilon-greedy for exploration
        if frame_count < epsilon_random_frames or EPSILON > np.random.rand(1)[0]:
            # Take random action
            action = np.random.choice(total_actions)
        else:
            # Predict action Q-values
            # From environment state
            state_tensor = tf.convert_to_tensor([state])
            action_probs = model(state_tensor, training=False)
            # Take best action
            action = tf.argmax(action_probs[0]).numpy()
        
        # Decay probability of taking random action
        EPSILON -= epsilon_interval / epsilon_greedy_frames
        EPSILON = max(EPSILON, EPSILON_MIN)
        
        # Apply the sampled action in our environment
        proto_state_next, reward, done = mercadoSecundario.step_dqn(proto_state, action)
        state_next = [proto_state_next.day_step, proto_state_next.cumulative_consumption, proto_state_next.cumulative_price, proto_state_next.agents_info['B1']['soc'], battery_capacity, proto_state_next.agents_info['B1']['chargeHistory'], proto_state_next.agents_info['B1']['dischargeHistory']] + energy_fixed_input.tolist()

        episode_reward += reward
        
        # Save actions and states in replay buffer
        action_history.append(action)
        state_history.append(state)
        state_next_history.append(state_next)
        done_history.append(done)
        rewards_history.append(reward)
        state       = state_next
        proto_state = proto_state_next
        # Update weights of the model
        if frame_count % update_after_actions == 0 and len(done_history) > BATCH_SIZE:
            #print("Training model")
            # Get indices of samples for replay buffers
            indices = np.random.choice(range(len(done_history)), size=BATCH_SIZE)
            
            # Using list comprehension to sample from replay buffer
            state_sample = np.array([state_history[i] for i in indices])
            state_next_sample = np.array([state_next_history[i] for i in indices])
            rewards_sample = [rewards_history[i] for i in indices]
            action_sample = [action_history[i] for i in indices]
            done_sample = tf.convert_to_tensor(
                [float(done_history[i]) for i in indices]
            )
            
            # Build the updated Q-values for the sampled future states
            # Use the target model for stability
            future_rewards = model_target.predict(state_next_sample, verbose=0)
            # Q value = reward + discount factor * expected future reward
            updated_q_values = rewards_sample + GAMMA * tf.reduce_max(
                future_rewards, axis=1
            )
            
            # If final frame set the last value to -1
            updated_q_values = updated_q_values * (1 - done_sample) - done_sample
            
            # Create a mask so we only calculate loss on the updated Q-values
            masks = tf.one_hot(action_sample, total_actions)
            
            with tf.GradientTape() as tape:
                # Train the model on the states and updated Q-values
                q_values = model(state_sample)
                
                # Apply the masks to the Q-values to get the Q-value for action taken
                q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
                # Calculate loss between new Q-value and old Q-value
                loss = loss_function(updated_q_values, q_action)
            
            # Backpropagation
            grads = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(grads, model.trainable_variables), verbose=0)


        if frame_count % update_target_network == 0:
            print("Updating target model")
            # update the target network with new weights
            model_target.set_weights(model.get_weights())
            # Log details
            template = "running reward: {:.2f} at episode {}, frame count {}"
            print(template.format(running_reward, episode_count, frame_count))
            model.save_weights(save_model_path + "model_episode_{}.h5".format(episode_count))
            model_target.save_weights(save_model_path + "model_target_episode_{}.h5".format(episode_count))
            dibujaGraficaQ()
            
        # Limit the state and reward history
        if len(rewards_history) > max_memory_length:
            del rewards_history[:1]
            del state_history[:1]
            del state_next_history[:1]
            del action_history[:1]
            del done_history[:1]
            
        if done: break
        
    # Update running reward to check condition for solving
    episode_reward_history.append(episode_reward)
    if len(episode_reward_history) > 100:
        del episode_reward_history[:1]
    running_reward = np.mean(episode_reward_history)
    
    episode_count += 1
    
    if running_reward > 40:  # Condition to consider the task solved
        print("Solved at episode {}!".format(episode_count))
        break
    
    if (
        MAX_EPISODES > 0 and episode_count >= MAX_EPISODES
    ):
        print("Stopped at episode {}!".format(episode_count))
        break

print(max(rewards_history))
