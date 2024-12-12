import csv
import os
import random

import pandas as pd

import matplotlib.pyplot as plt

from game import Yahtzee, YahtzeeAIBase
from state import State, Action, Category
from utils import calculate_probability, calculate_score
from constants import *


class QAction:
	def __init__(self, action: Action, action_value: tuple[int, ...] | Category | None = None):
		self.action = action
		match action:
			case Action.ROLL:
				self.action_value = None
			case Action.HOLD:
				self.action_value = tuple(sorted(die for die in action_value)) if action_value else None
			case Action.RELEASE:
				self.action_value = tuple(sorted(die for die in action_value)) if action_value else None
			case Action.SCORE:
				self.action_value = action_value if action_value else None

	def __eq__(self, other):
		return (self.action == other.action and
				self.action_value == other.action_value)

	def __hash__(self):
		return hash((self.action, self.action_value))

	def __str__(self):
		return f"Action: {self.action}, Action Value: {self.action_value}"


class StateKey:
	def __init__(self, state: State):
		self.dice_held = tuple(sorted(die for die in state.dice_held)) if state.dice_held else ()
		self.dice_on_table = tuple(sorted(die for die in state.dice_on_table)) if state.dice_on_table else ()
		self.rolls_left = state.rolls_left

	def __eq__(self, other):
		return (self.dice_held == other.dice_held and
				self.dice_on_table == other.dice_on_table and
				self.rolls_left == other.rolls_left)

	def __hash__(self):
		return hash((self.dice_held, self.dice_on_table, self.rolls_left))

	def __str__(self):
		return f"StateKey: Dice Held:{self.dice_held}, Dice On Table:{self.dice_on_table}, Rolls Left:{self.rolls_left}"


class QLearningYahtzee(YahtzeeAIBase):
	def __init__(self):
		self.alpha = ALPHA
		self.gamma = GAMMA
		self.epsilon = EPSILON
		self.epsilon_decay = EPSILON_DECAY
		self.min_epsilon = MIN_EPSILON
		self.q_table: dict[StateKey, dict[QAction, float]] = {}

	def get_q_value(self, state: State, q_action: QAction):
		state_key = StateKey(state)
		if state_key not in self.q_table:
			self.add_missing_state_to_table(state)
		return self.q_table[state_key][q_action]

	def get_max_q_value(self, state: State):
		state_key = StateKey(state)
		if state_key not in self.q_table:
			self.add_missing_state_to_table(state)
		return max(self.q_table[state_key].values())

	def add_missing_state_to_table(self, state: State):
		state_key = StateKey(state)
		if state_key not in self.q_table:
			self.q_table[state_key] = {}

		for action in self.get_possible_actions(state):
			match action:
				case Action.ROLL:
					if state.rolls_left == 0:
						continue
					self.q_table[state_key][QAction(action)] = 0
				case Action.HOLD:
					random_dice_to_hold = random.sample(state.dice_on_table,
														random.randint(1, max(1, len(state.dice_on_table) - 1)))
					self.q_table[state_key][QAction(action, action_value=tuple(random_dice_to_hold))] = 0
				case Action.RELEASE:
					random_dice_to_release = random.sample(state.dice_held,
														   random.randint(1, max(1, len(state.dice_held) - 1)))
					self.q_table[state_key][QAction(action, action_value=tuple(random_dice_to_release))] = 0
				case Action.SCORE:
					random_category = random.choice(
						[cat for cat, score in state.categories[state.turn].items() if score == -1])
					category_score = calculate_score(random_category, state.dice_on_table + state.dice_held)
					self.q_table[state_key][QAction(action, action_value=random_category)] = category_score

	def update_q_value(self, state: State, q_action: QAction, reward: int,
					   next_state: State):
		state_key = StateKey(state)
		next_state_key = StateKey(next_state)

		if next_state_key not in self.q_table:
			self.add_missing_state_to_table(next_state)

		if q_action not in self.q_table[state_key]:
			self.q_table[state_key][q_action] = 0

		best_next_q = 0
		if next_state_key in self.q_table:
			for next_q_action, q_value in self.q_table[next_state_key].items():
				if (next_q_action.action == q_action.action and
						next_q_action.action_value == q_action.action_value):
					best_next_q = q_value
					break

		current_q = self.get_q_value(state, q_action)
		new_q = current_q + self.alpha * (reward + self.gamma * best_next_q - current_q)
		self.q_table[state_key][q_action] = new_q
		return new_q

	def choose_action(self, state: State):
		if random.uniform(0, 1) < self.epsilon:
			action = random.choice(self.get_possible_actions(state))
			return action
		else:
			state_key = StateKey(state)
			if state_key not in self.q_table:
				self.add_missing_state_to_table(state)
			action = max(self.q_table[state_key], key=self.q_table[state_key].get).action
			if action not in self.get_possible_actions(state):
				self.q_table[state_key].pop(max(self.q_table[state_key], key=self.q_table[state_key].get))
				return random.choice(self.get_possible_actions(state))
			return action

	def choose_hold(self, state: State):
		def random_hold():
			dice_len = len(state.dice_on_table)
			dice_to_hold_len = random.randint(1, max(1, dice_len - 1))
			dice_to_hold = random.sample(state.dice_on_table, dice_to_hold_len)
			return dice_to_hold

		state_key = StateKey(state)
		if state_key not in self.q_table:
			self.add_missing_state_to_table(state)

		hold_actions = {action: q_value for action, q_value in self.q_table[state_key].items() if
						action.action == Action.HOLD}
		if not hold_actions:
			return random_hold()

		max_q_action = max(hold_actions, key=hold_actions.get)
		if max_q_action.action_value is None:
			return random_hold()

		dice_to_hold = [die for die in state.dice_on_table if die in max_q_action.action_value]
		if not dice_to_hold:
			return random_hold()

		return dice_to_hold

	def choose_release(self, state: State):
		def random_release():
			dice_len = len(state.dice_held)
			dice_to_release_len = random.randint(1, max(1, dice_len - 1))
			dice_to_release = random.sample(state.dice_held, dice_to_release_len)
			return dice_to_release

		state_key = StateKey(state)
		if state_key not in self.q_table:
			self.add_missing_state_to_table(state)

		release_actions = {action: q_value for action, q_value in self.q_table[state_key].items() if
						   action.action == Action.RELEASE}

		if not release_actions:
			return random_release()

		max_q_action = max(release_actions, key=release_actions.get)
		if max_q_action.action_value is None:
			return random_release()

		dice_to_release = [die for die in state.dice_held if die in max_q_action.action_value]
		if not dice_to_release:
			return random_release()

		return dice_to_release

	def choose_category(self, state: State) -> Category | None:
		state_key = StateKey(state)
		if state_key not in self.q_table:
			self.add_missing_state_to_table(state)
		available_categories = [cat for cat, score in state.categories[state.turn].items() if score == -1]
		max_q_value_category = max(self.q_table[state_key], key=self.q_table[state_key].get).action_value
		if max_q_value_category is None or max_q_value_category not in available_categories:
			return max(available_categories,
					   key=lambda x: calculate_score(x, state.dice_on_table + state.dice_held))
		return max_q_value_category

	def evaluate_hold(self, dice_held, dice_to_hold, remaining_rolls, scoring_categories):
		expected_scores = []
		new_dice_held = dice_held + list(dice_to_hold)
		for category in scoring_categories:
			probability = calculate_probability(category, new_dice_held, remaining_rolls)
			potential_score = calculate_score(category, new_dice_held)
			expected_scores.append(probability * potential_score)
		return sum(expected_scores)

	def evaluate_release(self, dice_held, dice_to_release, remaining_rolls, scoring_categories):
		remaining_dice = [die for die in dice_held if die not in dice_to_release]
		expected_scores = []
		for category in scoring_categories:
			probability = calculate_probability(category, remaining_dice, remaining_rolls)
			potential_score = calculate_score(category, remaining_dice)
			expected_scores.append(probability * potential_score)
		return sum(expected_scores)

	def save_q_table(self):
		with open(Q_TABLE_FILE, mode='w', newline='') as file:
			writer = csv.writer(file)
			writer.writerow(["Dice Held", "Dice On Table", "Rolls Left", "Action", "Action Value", "Q-Value"])
			for state_key, q_values in self.q_table.items():
				for q_action, q_value in q_values.items():
					writer.writerow(
						[state_key.dice_held, state_key.dice_on_table, state_key.rolls_left, q_action.action,
						 q_action.action_value, q_value])

	def load_q_table(self):
		if os.path.exists(Q_TABLE_FILE):
			df = pd.read_csv(Q_TABLE_FILE)
			for index, row in df.iterrows():
				state_key = StateKey(State(row["Dice Held"], row["Dice On Table"], row["Rolls Left"]))
				action_value = row["Action Value"] if not pd.isna(row["Action Value"]) else None
				action = Action.to_action(row["Action"])
				q_action = QAction(action, action_value)
				if state_key not in self.q_table:
					self.q_table[state_key] = {}
				self.q_table[state_key][q_action] = row["Q-Value"]

	def print_q_table(self):
		i = 0
		for state_key, q_values in self.q_table.items():
			print(f"State:{i}")
			print("Dice Held:", state_key.dice_held)
			print("Dice On Table:", state_key.dice_on_table)
			print("Rolls Left:", state_key.rolls_left)
			print(f"Q-Values{i}:")
			j = 0
			for q_action, q_value in q_values.items():
				print(f"Action{j}: ", q_action.action)
				print(f"Action Value: ", q_action.action_value)
				print("Q-Value: ", q_value)
				j += 1
			i += 1

	def evaluate_reward(self, state: State, q_action: QAction, previous_action: Action,
						scoring_categories: list[Category]) -> int:
		reward = 0
		match q_action.action:
			case Action.ROLL:
				if previous_action == Action.HOLD or previous_action == Action.RELEASE:
					reward += 10
				if state.rolls_left == 2:
					reward -= 10
			case Action.HOLD:
				if previous_action == Action.HOLD or previous_action == Action.RELEASE:
					reward -= 10
				if state.rolls_left == 2:
					reward += 10
				if q_action.action_value and len(q_action.action_value) == len(state.dice_on_table):
					reward -= 10
				reward += self.evaluate_hold(state.dice_held, q_action.action_value, state.rolls_left,
											 scoring_categories)
			case Action.RELEASE:
				if previous_action == Action.RELEASE or previous_action == Action.HOLD:
					reward -= 10
				if state.rolls_left == 2:
					reward += 10
				if q_action.action_value and len(q_action.action_value) == len(state.dice_held):
					reward -= 25
				reward += self.evaluate_release(state.dice_held, q_action.action_value, state.rolls_left,
												scoring_categories)
			case Action.SCORE:
				if previous_action == Action.HOLD or previous_action == Action.RELEASE:
					reward -= 10
				if state.rolls_left == 2:
					reward -= 10
				reward += calculate_score(q_action.action_value, state.dice_on_table + state.dice_held)
		return reward

	def train(self, num_episodes=1000, max_turns=24):
		q_values = []
		for episode in range(num_episodes):
			game = Yahtzee(self)
			state = game.state
			previous_action = None
			nr_of_rolls_per_turn = 0
			rewards_per_episode = []
			total_reward = 0

			for turn in range(max_turns):
				reward = 0
				scoring_categories = game.get_available_categories()
				action = self.choose_action(state)
				q_action = None
				match action:
					case Action.ROLL:
						nr_of_rolls_per_turn += 1
						game.roll()
						q_action = QAction(action)

					case Action.HOLD:
						dice_to_hold = self.choose_hold(state)
						for die in dice_to_hold:
							game.hold(state.dice_on_table.index(die))
						q_action = QAction(action, action_value=tuple(dice_to_hold))

					case Action.RELEASE:
						dice_to_release = self.choose_release(state)
						for die in dice_to_release:
							game.release(state.dice_held.index(die))
						q_action = QAction(action, action_value=tuple(state.dice_held))

					case Action.SCORE:
						category = self.choose_category(state)
						q_action = QAction(action, action_value=category)

				reward += self.evaluate_reward(state, q_action, previous_action, scoring_categories)
				total_reward += reward
				next_state = game.state
				q_value = self.update_q_value(state, q_action, reward, next_state)
				q_values.append(q_value)
				state = next_state
				previous_action = action
				nr_of_rolls_per_turn = 0

			self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

			if (episode + 1) % 1000 == 0:
				print(f"Episode {episode + 1}: Total Reward = {reward}, Epsilon = {self.epsilon}")
			rewards_per_episode.append(total_reward)

		print("Training complete!")
		plot_rewards(q_values)
		self.save_q_table()


def plot_rewards(rewards):
	plt.figure(figsize=(10, 6))
	plt.plot(rewards, label='Reward per Episode', color='blue')
	plt.xlabel('Episode')
	plt.ylabel('Cumulative Reward')
	plt.title('Reward vs. Episode')
	plt.legend()
	plt.grid(True)
	plt.show()
