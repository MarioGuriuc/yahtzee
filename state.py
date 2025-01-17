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

	@staticmethod
	def to_action(action_str: str):
		match action_str:
			case "Action.ROLL":
				return Action.ROLL
			case "Action.HOLD":
				return Action.HOLD
			case "Action.RELEASE":
				return Action.RELEASE
			case "Action.SCORE":
				return Action.SCORE


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
	def __init__(self, dice_held: list[int] = None, dice_on_table: list[int] = None, rolls_left: int = None):
		self.state_type: StateType = StateType.INITIAL
		self.turn: int = 0
		self.score: dict[int, int] = {0: 0, 1: 0}
		self.rolls_left: int = 3 if rolls_left is None else rolls_left
		self.dice_held: list[int] = dice_held if dice_held else []
		self.dice_on_table: list[int] = dice_on_table if dice_on_table else [1, 2, 3, 4, 5]
		self.categories: list[dict[Category, int]] = [empty_category_dict.copy(), empty_category_dict.copy()]

	def __str__(self):
		return f"State(turn={self.turn}, score={self.score}, rolls_left={self.rolls_left}, dice_held={self.dice_held}, dice_on_table={self.dice_on_table}, categories={self.categories})"
