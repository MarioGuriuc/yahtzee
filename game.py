import secrets
from abc import ABC, abstractmethod
from state import *
import random


class YahtzeeAIBase(ABC):
	@abstractmethod
	def choose_action(self, state: State) -> Action:
		pass

	@abstractmethod
	def choose_category(self, state: State) -> Category:
		pass

	@abstractmethod
	def choose_hold(self, dice_on_table: list[int]) -> list[int]:
		pass

	@abstractmethod
	def choose_release(self, dice_held: list[int]) -> list[int]:
		pass

	@staticmethod
	def get_possible_actions(state: State) -> list[Action]:
		actions = []
		if state.rolls_left == 0:
			return [Action.SCORE]
		if state.rolls_left == 3:
			return [Action.ROLL]

		if state.rolls_left > 0:
			actions.append(Action.ROLL)
		if len(state.dice_on_table) > 0 and state.rolls_left < 3:
			actions.append(Action.HOLD)
		if len(state.dice_held) != 0:
			actions.append(Action.RELEASE)

		actions.append(Action.SCORE)

		return actions


class RandomYahtzeeAI(YahtzeeAIBase):
	def choose_action(self, state: State) -> Action:
		return secrets.choice(self.get_possible_actions(state))

	def choose_category(self, state: State) -> Category:
		available_categories = [cat for cat, score in state.categories[state.turn].items() if score == -1]
		return secrets.choice(available_categories) if available_categories else None

	def choose_hold(self, dice_on_table: list[int]) -> list[int]:
		return random.sample(dice_on_table, random.randint(0, len(dice_on_table) - 1)) if dice_on_table else []

	def choose_release(self, dice_held: list[int]) -> list[int]:
		return random.sample(dice_held, random.randint(0, len(dice_held) - 1)) if dice_held else []


class Yahtzee:
	def __init__(self, ai: YahtzeeAIBase):
		self.state = State()
		self.ai = ai

	def roll(self):
		self.state.state_type = StateType.ROLLING
		self.state.rolls_left -= 1
		self.state.dice_on_table = [random.randint(1, 6) for _ in range(len(self.state.dice_on_table))]

	def hold(self, index: int):
		self.state.dice_held.append(self.state.dice_on_table.pop(index))

	def release(self, index: int):
		self.state.dice_on_table.append(self.state.dice_held.pop(index))

	def score(self, category: Category):
		if self.state.categories[self.state.turn][category] != -1:
			return
		score = self.calculate_score(category)
		self.state.categories[self.state.turn][category] = score
		self.state.score[self.state.turn] += score
		return score

	def calculate_score(self, category: Category) -> int:
		dice = self.state.dice_on_table + self.state.dice_held
		match category:
			case Category.ONES:
				return dice.count(1)
			case Category.TWOS:
				return dice.count(2) * 2
			case Category.THREES:
				return dice.count(3) * 3
			case Category.FOURS:
				return dice.count(4) * 4
			case Category.FIVES:
				return dice.count(5) * 5
			case Category.SIXES:
				return dice.count(6) * 6
			case Category.THREE_OF_A_KIND:
				return sum(dice) if any(dice.count(x) >= 3 for x in set(dice)) else 0
			case Category.FOUR_OF_A_KIND:
				return sum(dice) if any(dice.count(x) >= 4 for x in set(dice)) else 0
			case Category.FULL_HOUSE:
				return 25 if sorted([dice.count(x) for x in set(dice)]) == [2, 3] else 0
			case Category.SMALL_STRAIGHT:
				if {1, 2, 3, 4}.issubset(dice) or {2, 3, 4, 5}.issubset(dice) or {3, 4, 5, 6}.issubset(dice):
					return 30
				return 0
			case Category.LARGE_STRAIGHT:
				if set(dice) == {1, 2, 3, 4, 5} or set(dice) == {2, 3, 4, 5, 6}:
					return 40
				return 0
			case Category.YAHTZEE:
				return 50 if len(set(dice)) == 1 else 0
			case Category.CHANCE:
				return sum(dice)
		return 0

	def end_turn(self):
		self.state.state_type = StateType.INITIAL
		self.state.turn = 1 - self.state.turn
		self.state.rolls_left = 3
		self.state.dice_held = []
		self.state.dice_on_table = [1, 2, 3, 4, 5]

	def is_game_finished(self) -> bool:
		for category, score in self.state.categories[1 - self.state.turn].items():
			if score == -1:
				return False
		return True

	def reset(self):
		self.state = State()
