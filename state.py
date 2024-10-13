from enum import Enum


class StateType(Enum):
    INITIAL = 0
    ROLLING = 1
    HOLDING = 2
    SCORING = 3
    END_OF_TURN = 4
    FINAL = 5


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
    "CHANCE": Category.CHANCE
}

empty_category_dict = {
    Category.ONES: -1,
    Category.TWOS: -1,
    Category.THREES: -1,
    Category.FOURS: -1,
    Category.FIVES: -1,
    Category.SIXES: -1,
    Category.THREE_OF_A_KIND: -1,
    Category.FOUR_OF_A_KIND: -1,
    Category.FULL_HOUSE: -1,
    Category.SMALL_STRAIGHT: -1,
    Category.LARGE_STRAIGHT: -1,
    Category.YAHTZEE: -1,
    Category.CHANCE: -1
}


class State:
    def __init__(self):
        self.state_type: StateType = StateType.INITIAL
        self.turn: int = 0
        self.score: dict[int, int] = {0: 0, 1: 0}
        self.rolls_left: int = 3
        self.dice_held: list[int] = []
        self.dice_on_table: list[int] = [1, 2, 3, 4, 5]
        self.categories: list[dict[Category, int]] = [empty_category_dict.copy(), empty_category_dict.copy()]
