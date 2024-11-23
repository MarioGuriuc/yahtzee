from game import *
import numpy as np


import random
import secrets
import numpy as np
from game import *
from abc import ABC, abstractmethod
from state import *


class QLearningYahtzee(YahtzeeAIBase):
    def __init__(self):
        self.alpha = 0.9
        self.gamma = 0.95
        self.epsilon = 1
        self.epsilon_decay = 0.9995
        self.min_epsilon = 0.01
        self.q_table = {}

    def get_q_value(self, state: State, action: Action):
        state_tuple = state.get_state_tuple()
        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = np.zeros(4)  # Four actions: ROLL, HOLD, RELEASE, SCORE
        return self.q_table[state_tuple][action.value]

    def update_q_value(self, state: State, action: Action, reward: float, next_state: State):
        state_tuple = state.get_state_tuple()
        next_state_tuple = next_state.get_state_tuple()

        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = np.zeros(4)
        if next_state_tuple not in self.q_table:
            self.q_table[next_state_tuple] = np.zeros(4)

        future_q_value = np.max(self.q_table[next_state_tuple])

        self.q_table[state_tuple][action.value] += self.alpha * (reward + self.gamma * future_q_value - self.q_table[state_tuple][action.value])

    def decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def choose_action(self, state: State) -> Action:
        if np.random.rand() < self.epsilon:
            return np.random.choice([Action.ROLL, Action.HOLD, Action.RELEASE, Action.SCORE])
        else:
            state_tuple = state.get_state_tuple()
            if state_tuple not in self.q_table:
                self.q_table[state_tuple] = np.zeros(4)
            return np.argmax(self.q_table[state_tuple])

    def choose_category(self, state: State) -> Category:
        available_categories = [cat for cat, score in state.categories[state.turn].items() if score == -1]
        return secrets.choice(available_categories) if available_categories else None

    def choose_hold(self, state: State) -> list[int]:
        # Use Q-values to choose which dice to hold
        hold_decision = []
        for die in state.dice_on_table:
            # Get the Q-value for holding each dice
            q_value = self.get_q_value(state, Action.HOLD)  # Action for holding dice, consider each dice individually
            
            if np.random.rand() < self.epsilon:  # Exploration (randomly decide to hold or not)
                if np.random.rand() < 0.5:  # Arbitrary exploration chance for each dice
                    hold_decision.append(die)
            else:  # Exploitation (choose based on Q-values)
                if q_value > 0:  # If the Q-value suggests that holding this die is beneficial
                    hold_decision.append(die)
        
        return hold_decision

    def choose_release(self, state: State) -> list[int]:
        # Use Q-values to choose which dice to release
        release_decision = []
        for die in state.dice_held:
            # Get the Q-value for releasing each die
            q_value = self.get_q_value(state, Action.RELEASE)  # You could also modify this to evaluate individual dice
            
            if np.random.rand() < self.epsilon:  # Exploration (randomly decide to release or not)
                if np.random.rand() < 0.5:  # Arbitrary exploration chance for each die
                    release_decision.append(die)
            else:  # Exploitation (choose based on Q-values)
                if q_value > 0:  # If the Q-value suggests that releasing this die is beneficial
                    release_decision.append(die)

        return release_decision


def train_ai(ai: QLearningYahtzee, num_episodes: int, max_turns: int = 100):
    # Loop through the number of episodes (games)
    for episode in range(num_episodes):
        game = Yahtzee(ai)
        state = game.state
        
        # Start the game
        total_reward = 0
        
        # Loop through turns
        for turn in range(max_turns):
            if game.is_game_finished():
                break  # Game is finished
            
            state = game.state
            action = ai.choose_action(state)
            
            if action == Action.ROLL:
                game.roll()
            elif action == Action.HOLD:
                dice_to_hold = ai.choose_hold(state)
                for dice in dice_to_hold:
                    game.hold(state.dice_on_table.index(dice))
            elif action == Action.RELEASE:
                dice_to_release = ai.choose_release(state)
                for dice in dice_to_release:
                    game.release(state.dice_held.index(dice))
            elif action == Action.SCORE:
                category = ai.choose_category(state)
                if category:
                    score = game.score(category)
                    total_reward += score  # Reward is the score obtained for a valid action
            
            # Get the next state after the action
            next_state = game.state
            reward = total_reward  # You can adjust the reward structure as needed
            
            # Update Q-values using the current and next state
            ai.update_q_value(state, action, reward, next_state)
            
            # Decay epsilon after each turn to favor exploitation over time
            ai.decay_epsilon()

        print(f"Episode {episode + 1} completed with total score: {total_reward}") if episode % 100 == 0 else None
    print("Training complete!")
