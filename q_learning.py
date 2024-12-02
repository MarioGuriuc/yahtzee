import copy
import csv
import itertools
import os
import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import numpy as np

from constants import *
from game import *
from state import *

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
        state_tuple = state.get_state_tuple()
        self.update_q_state_tuple(state)
        return self.q_table[state_tuple][action.value]
    
    def get_max_q_value(self, state: State) -> float:
        state_tuple = state.get_state_tuple()
        self.update_q_state_tuple(state)
        return np.max(self.q_table[state_tuple])
    
    def update_q_state_tuple(self,state: State):
        state_tuple = state.get_state_tuple()
        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = np.zeros(len(Action))

    def update_q_value(self, state: State, action: Action, reward: float, next_state: State):
        state_tuple = state.get_state_tuple()
        self.update_q_state_tuple(state)

        max_future_q = self.get_max_q_value(next_state)
        current_q = self.get_q_value(state, action)

        self.q_table[state_tuple][action.value] = current_q + self.alpha * (
            reward + self.gamma * max_future_q - current_q
        )

    def decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
    
    def choose_action(self, state: State) -> Action:
        if np.random.rand() < self.epsilon:
            return random.choice(self.get_possible_actions(state))
        else:
            state_tuple = state.get_state_tuple()
            self.update_q_state_tuple(state)
            return Action(np.argmax(self.q_table[state_tuple]))
    
    def choose_category(self, state: State) -> Category | None:
        available_categories = [
            (cat, state.calculate_score(cat))
            for cat, score in state.categories[state.turn].items()
            if score == -1
        ]
        if not available_categories:
            return None
        return max(available_categories, key=lambda x: x[1])[0]
    
    def choose_hold(self, state: State) -> list[int]:
        all_dice = state.dice_on_table
        best_hold = []
        max_q_value = float('-inf')
        
        q_table_index = defaultdict(list)
        for state_tuple, q_values in self.q_table.items():
            _, table_dice, held_dice = state_tuple
            combined_dice = tuple(sorted(table_dice + held_dice))
            q_table_index[combined_dice].append((state_tuple, q_values))
        
        def process_subset(subset):
            nonlocal max_q_value, best_hold
            subset_set = set(subset)
            
            for combined_dice, states in q_table_index.items():
                if subset_set.issubset(combined_dice):
                    for state_tuple, q_values in states:
                        q_value = max(q_values)
                        if q_value > max_q_value:
                            max_q_value = q_value
                            best_hold = list(subset)
        
        subsets = [list(subset) for r in range(len(all_dice) + 1)
                   for subset in itertools.combinations(all_dice, r)]
        with ThreadPoolExecutor() as executor:
            executor.map(process_subset, subsets)
        
        if not best_hold:
            dices_to_hold = self.choose_best_dice_based_on_left_categories(state.categories[0])
            
            dice_counts = {die: all_dice.count(die) for die in dices_to_hold}
            most_common_dice = sorted(dice_counts.items(), key=lambda x: x[1], reverse=True)
            
            for die, count in most_common_dice:
                best_hold += [die] * count
        
        return best_hold
    
    def choose_best_dice_based_on_left_categories(self, categories_left: dict) -> list[int]:
        dice = []
        if categories_left[Category.SIXES] == -1:
            dice.append(6)
        elif categories_left[Category.FIVES] == -1:
            dice.append(5)
        elif categories_left[Category.FOURS] == -1:
            dice.append(4)
        elif categories_left[Category.THREES] == -1:
            dice.append(3)
        elif categories_left[Category.TWOS] == -1:
            dice.append(2)
        elif categories_left[Category.ONES] == -1:
            dice.append(1)
        return dice
    
    def choose_release(self, state: State) -> list[int]:
        dice_held = state.dice_held
        best_release = []
        max_q_value = float('-inf')
        
        q_table_index = defaultdict(list)
        for state_tuple, q_values in self.q_table.items():
            _, table_dice, held_dice = state_tuple
            combined_dice = tuple(sorted(table_dice + held_dice))
            q_table_index[combined_dice].append((state_tuple, q_values))
        
        def process_subset(subset):
            nonlocal max_q_value, best_release
            subset_set = set(subset)
            
            for combined_dice, states in q_table_index.items():
                if subset_set.issubset(combined_dice):
                    for state_tuple, q_values in states:
                        q_value = q_values[Action.RELEASE]
                        if q_value > max_q_value:
                            max_q_value = q_value
                            best_release = list(subset)
        
        subsets = [list(subset) for r in range(len(dice_held) + 1)
                   for subset in itertools.combinations(dice_held, r)]
        with ThreadPoolExecutor() as executor:
            executor.map(process_subset, subsets)
        
        if not best_release:
            best_release = []
        
        return best_release
    
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
    
    def train(self, num_episodes: int = 1000, max_turns: int = 24, num_threads: int = 4):
        lock = threading.Lock()
        total_rewards = [0] * num_episodes
        total_scores = [0] * num_episodes
    
        def train_in_thread(thread_id: int, start_episode: int, end_episode: int):
            nonlocal total_rewards
            nonlocal total_scores
            local_ai = copy.deepcopy(self)
            for episode in range(start_episode, end_episode):
                game = Yahtzee(local_ai)
                state = game.state
                total_reward = 0
                total_score = 0
    
                for turn in range(max_turns):
    
                    action = local_ai.choose_action(state)
                    reward = 0
    
                    match action:
                        case Action.ROLL:
                            game.roll()
    
                        case Action.HOLD:
                            dice_to_hold = local_ai.choose_hold(state)
                            if not dice_to_hold:
                                reward += -5
                            else:
                                for die in dice_to_hold:
                                    game.hold(state.dice_on_table.index(die))
                                reward += 2 * len(dice_to_hold)
    
                        case Action.RELEASE:
                            dice_to_release = local_ai.choose_release(state)
                            for die in dice_to_release:
                                game.release(state.dice_held.index(die))
                            reward += -2 * len(dice_to_release)
    
                        case Action.SCORE:
                            category = local_ai.choose_category(state)
                            if category:
                                reward += game.state.score[0]
                            else:
                                reward = -10
    
                    next_state = game.state
    
                    with lock:
                        self.update_q_value(state, action, reward, next_state)
    
                    total_reward += reward
                    state = next_state
                    local_ai.decay_epsilon()
    
                total_rewards[episode] = total_reward
                total_scores[episode] = game.state.score[0]
                write_to_csv("q_learning.csv", thread_id, episode+1, total_reward, total_score, local_ai.epsilon)
                if (episode + 1) % 100 == 0:
                    print(f"Thread {thread_id}: Episode {episode + 1}, Reward: {total_reward},Epsilon: {local_ai.epsilon}")
    
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


def write_to_csv(file_name, thread, episode, reward, score, epsilon):
    write_header = not os.path.isfile(file_name)
    
    with open(file_name, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        if write_header:
            writer.writerow(["Thread", "Episode", "Reward", "Score", "Epsilon"])
        
        writer.writerow([thread, episode, reward, score, epsilon])





