from enum import Enum


class StateType(Enum):
	INITIAL = 0
	ROLLING = 1
	FINAL = 2


class Action(Enum):
	ROLL = 0
	HOLD = 1
	RELEASE = 2
	SCORE = 3
	
class HoldOption(Enum):
	HOLD0 = 0
	HOLD1 = 1
	HOLD2 = 2
	HOLD3 = 3
	HOLD4 = 4

class ReleaseOption(Enum):
	RELEASE0 = 0
	RELEASE1 = 1
	RELEASE2 = 2
	RELEASE3 = 3
	RELEASE4 = 4


class Category(Enum):
	ONES = 1
	TWOS = 2
	THREES = 3
	FOURS = 4
	FIVES = 5
	SIXES = 6
	THREE_OF_A_KIND = 7
	FOUR_OF_A_KIND = 8
	FULL_HOUSE = 9
	SMALL_STRAIGHT = 10
	LARGE_STRAIGHT = 11
	CHANCE = 12
	YAHTZEE = 13


categories = {
	"ONES": Category.ONES,
	"TWOS": Category.TWOS,
	"THREES": Category.THREES,
	"FOURS": Category.FOURS,
	"FIVES": Category.FIVES,
	"SIXES": Category.SIXES,
	"THREE_OF_A_KIND": Category.THREE_OF_A_KIND,
	"FOUR_OF_A_KIND": Category.FOUR_OF_A_KIND,
	"FULL_HOUSE": Category.FULL_HOUSE,
	"SMALL_STRAIGHT": Category.SMALL_STRAIGHT,
	"LARGE_STRAIGHT": Category.LARGE_STRAIGHT,
	"YAHTZEE": Category.YAHTZEE,
	"CHANCE": Category.CHANCE,

}

empty_category_dict = {cat: -1 for cat in Category}


class State:
	def __init__(self):
		self.state_type: StateType = StateType.INITIAL
		self.turn: int = 0
		self.score: dict[int, int] = {0: 0, 1: 0}
		self.rolls_left: int = 3
		self.dice_held: list[int] = []
		self.dice_on_table: list[int] = [1, 2, 3, 4, 5]
		self.categories: list[dict[Category, int]] = [empty_category_dict.copy(), empty_category_dict.copy()]
  
	def get_state_tuple(self):
		return self.rolls_left, tuple(self.dice_on_table), tuple(self.dice_held)
	
	def calculate_score(self,Category):
		dice = self.dice_on_table + self.dice_held
		if Category == Category.ONES:
			return dice.count(1)
		elif Category == Category.TWOS:
			return dice.count(2) * 2
		elif Category == Category.THREES:
			return dice.count(3) * 3
		elif Category == Category.FOURS:
			return dice.count(4) * 4
		elif Category == Category.FIVES:
			return dice.count(5) * 5
		elif Category == Category.SIXES:
			return dice.count(6) * 6
		elif Category == Category.THREE_OF_A_KIND:
			return sum(dice) if any(dice.count(x) >= 3 for x in set(dice)) else 0
		elif Category == Category.FOUR_OF_A_KIND:
			return sum(dice) if any(dice.count(x) >= 4 for x in set(dice)) else 0
		elif Category == Category.FULL_HOUSE:
			return 25 if sorted([dice.count(x) for x in set(dice)]) == [2, 3] else 0
		elif Category == Category.SMALL_STRAIGHT:
			if {1, 2, 3, 4}.issubset(dice) or {2, 3, 4, 5}.issubset(dice) or {3, 4, 5, 6}.issubset(dice):
				return 30
			return 0
		elif Category == Category.LARGE_STRAIGHT:
			if set(dice) == {1, 2, 3, 4, 5} or set(dice) == {2, 3, 4, 5, 6}:
				return 40
			return 0
		elif Category == Category.YAHTZEE:
			return 50 if len(set(dice)) == 1 else 0
		elif Category == Category.CHANCE:
			return sum(dice)
		return 0
	
	def clone(self):
		new_state = State()
		new_state.state_type = self.state_type
		new_state.turn = self.turn
		new_state.score = self.score.copy()
		new_state.rolls_left = self.rolls_left
		new_state.dice_held = self.dice_held.copy()
		new_state.dice_on_table = self.dice_on_table.copy()
		new_state.categories = [cat.copy() for cat in self.categories]
		return new_state
