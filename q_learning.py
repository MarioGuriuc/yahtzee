import csv
import itertools
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from game import *
from state import *
from utils import *

ALPHA = 0.5
GAMMA = 0.9
EPSILON = 1.0
EPSILON_DECAY = 0.9999
MIN_EPSILON = 0.1
Q_TABLE = {}
Q_TABLE_FILE = "q_table.csv"

class QLearningYahtzee(YahtzeeAIBase):
    def __init__(self):
        self.alpha = ALPHA
        self.gamma = GAMMA
        self.epsilon = EPSILON
        self.epsilon_decay = EPSILON_DECAY
        self.min_epsilon = MIN_EPSILON
        self.q_table = {}
        self.q_table_file = Q_TABLE_FILE

    def get_q_value(self, state: State, action: Action) -> float:
        state_tuple = self.update_q_state_tuple(state)
        return self.q_table[state_tuple][action.value]
    
    def get_max_q_value(self, state: State) -> float:
        state_tuple = self.update_q_state_tuple(state)
        return np.max(self.q_table[state_tuple])
    
    def update_q_state_tuple(self,state: State):
        state_tuple = state.get_state_tuple()
        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = np.zeros(len(Action))
        return state_tuple

    def update_q_value(self, state: State, action: Action, reward: float, next_state: State):
        state_tuple = self.update_q_state_tuple(state)

        max_future_q = self.get_max_q_value(next_state)
        current_q = self.get_q_value(state, action)
        
        self.decay_epsilon()

        self.q_table[state_tuple][action.value] = current_q + self.alpha * (
            reward + self.gamma * max_future_q - current_q
        )

    def decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
    
    def choose_action(self, state: State) -> Action:
        poss_actions = self.get_possible_actions(state)
        if np.random.rand() < self.epsilon:
            return secrets.choice(poss_actions)
        else:
            self.update_q_state_tuple(state)
            for state_tuple, q_values in self.q_table.items():
                action = Action(np.argmax(q_values))
            return action if action in poss_actions else random.choice(poss_actions)
    
    def choose_category(self, state: State) -> Category | None:
        available_categories = [
            (cat, state.calculate_score(cat))
            for cat, score in state.categories[state.turn].items()
            if score == -1
        ]

        return max(available_categories, key=lambda x: x[1])[0]
    
    def choose_hold(self, state: State) -> list[int]:
        hold_decision = []
        for die in state.dice_on_table:
            q_value = self.get_q_value(state, Action.HOLD)
            
            if np.random.rand() < self.epsilon:
                if np.random.rand() < 0.5:
                    hold_decision.append(die)
            else:
                if q_value > 0:
                    hold_decision.append(die)
        rnd = secrets.choice(list(itertools.combinations(state.dice_on_table, secrets.choice(range(1, len(state.dice_on_table) + 1)))))
        return hold_decision if len(hold_decision) != 0 else rnd

    def choose_release(self, state: State) -> list[int]:
        best_release = []
        for die in state.dice_held:
            q_value = self.get_q_value(state, Action.RELEASE)
            
            if np.random.rand() < self.epsilon:
                if np.random.rand() < 0.5:
                    best_release.append(die)
            else:
                if q_value > 0:
                    best_release.append(die)
        rnd = secrets.choice(list(itertools.combinations(state.dice_held, secrets.choice(range(1, len(state.dice_held) + 1)))))
        return best_release if len(best_release) != 0 else rnd
    
    def save_q_table(self):
        rows = []
        for state_tuple, q_values in self.q_table.items():
            row = list(state_tuple) + list(q_values)
            rows.append(row)
        
        columns = [f"State_{i}" for i in range(len(rows[0]) - len(Action))] + [
                f"Q_Action_{action.name}" for action in Action
        ]
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(self.q_table_file, index=False)
        print("Q-table saved to", self.q_table_file)
    
    def load_q_table(self):
        df = pd.read_csv(self.q_table_file)
        for _, row in df.iterrows():
            state_tuple = tuple(row[f"State_{i}"] for i in range(len(row) - len(Action)))
            q_values = row[[f"Q_Action_{action.name}" for action in Action]].values
            self.q_table[state_tuple] = q_values
        print("Q-table loaded from", self.q_table_file)
        
    def evaluate_hold(self, dice_held, dice_to_hold, remaining_rolls, scoring_categories):
        expected_scores = []
        new_dice_held = dice_held + list(dice_to_hold)
        for category in scoring_categories:
            probability = calculate_probability(category, new_dice_held, remaining_rolls)
            potential_score = calculate_score(category, new_dice_held)
            expected_scores.append(probability * potential_score)
        return max(expected_scores)

    def evaluate_release(self, dice_held, dice_to_release, remaining_rolls, scoring_categories):
        remaining_dice = [die for die in dice_held if die not in dice_to_release]
        expected_scores = []
        for category in scoring_categories:
            probability = calculate_probability(category, remaining_dice, remaining_rolls)
            potential_score = calculate_score(category, remaining_dice)
            expected_scores.append(probability * potential_score)
        return max(expected_scores)
    
    def train(self, num_episodes: int = 1000, max_turns: int = 24, num_threads: int = 4):
        lock = threading.Lock()
        total_rewards = [0] * num_episodes
        total_scores = [0] * num_episodes
        
        def train_in_thread(thread_id: int, start_episode: int, end_episode: int):
            nonlocal total_rewards
            nonlocal total_scores
            local_ai = self
            for episode in range(start_episode, end_episode):
                game = Yahtzee(local_ai)
                state = game.state
                total_reward = 0
                total_score = 0
                scoring_categories = game.get_available_categories()
                
                for turn in range(max_turns):
                    with lock:
                        action = local_ai.choose_action(state)
                    reward = 0
                    
                    match action:
                        case Action.ROLL:
                            game.roll()
                        
                        case Action.HOLD:
                            dice_to_hold = local_ai.choose_hold(state)
                            reward = self.evaluate_hold(state.dice_held, dice_to_hold, state.rolls_left,
                                                        scoring_categories)
                            for die in dice_to_hold:
                                game.hold(state.dice_on_table.index(die))
                        
                        case Action.RELEASE:
                            dice_to_release = local_ai.choose_release(state)
                            reward = self.evaluate_release(state.dice_held, dice_to_release, state.rolls_left,
                                                           scoring_categories)
                            for die in dice_to_release:
                                game.release(state.dice_held.index(die))
                        
                        case Action.SCORE:
                            category = local_ai.choose_category(state)
                            if category:
                                score = game.calculate_score(category)
                                reward = score if score > 0 else -100
                            else:
                                reward = -100
                    
                    next_state = game.state
                    
                    with lock:
                        self.update_q_value(state, action, reward, next_state)
                    
                    total_reward += reward
                    state = next_state
                
                total_rewards[episode] = total_reward
                total_scores[episode] = game.state.score[0]
                write_to_csv("q_learning.csv", thread_id, episode + 1, total_reward, total_score, local_ai.epsilon)
                if (episode + 1) % 100 == 0:
                    print(
                        f"Thread {thread_id}: Episode {episode + 1}, Reward: {total_reward},Epsilon: {local_ai.epsilon}")
        
        episodes_per_thread = num_episodes // num_threads
        extra_episodes = num_episodes % num_threads
        
        ranges = []
        start = 0
        for i in range(num_threads):
            end = start + episodes_per_thread + (1 if i < extra_episodes else 0)
            ranges.append((start, end))
            start = end
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                    executor.submit(train_in_thread, i, start, end)
                    for i, (start, end) in enumerate(ranges)
            ]
            
            for future in futures:
                future.result()
        
        print("Multithreaded training complete!")
        plot_rewards(total_rewards)


def write_to_csv(file_name, thread, episode, reward, score, epsilon):
    write_header = not os.path.isfile(file_name)
    
    with open(file_name, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        if write_header:
            writer.writerow(["Thread", "Episode", "Reward", "Score", "Epsilon"])
        
        writer.writerow([thread, episode, reward, score, epsilon])

def moving_average(data, window_size=10):
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def plot_rewards(rewards):
    plt.figure(figsize=(10, 6))
    plt.plot(rewards, label='Reward per Episode', color='blue')
    plt.xlabel('Episode')
    plt.ylabel('Cumulative Reward')
    plt.title('Reward vs. Episode')
    plt.legend()
    plt.grid(True)
    plt.show()
