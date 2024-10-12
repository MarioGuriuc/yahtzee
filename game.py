from state import *
import random

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


def match_str_to_category(category: str) -> Category:
    return categories[category]


class Yahtzee:
    def __init__(self):
        self.state = State()

    def roll(self):
        print("Player", self.state.turn + 1, " rolled")
        self.state.state_type = StateType.ROLLING
        self.state.rolls_left -= 1
        self.state.dice_on_table = [random.randint(1, 6) for _ in range(5)]
        print("Rolls left:", self.state.rolls_left)
        print("Dice on table:", self.state.dice_on_table)
        print("Dice held:", self.state.dice_held)
        if self.state.rolls_left == 0:
            self.state.state_type = StateType.HOLDING

    def hold(self, index: int):
        self.state.dice_held.append(self.state.dice_on_table[index])
        self.state.dice_on_table.pop(index)
        print("Dice on table:", self.state.dice_on_table)
        print("Dice held:", self.state.dice_held)

    def release(self, index: int):
        self.state.dice_on_table.append(self.state.dice_held[index])
        self.state.dice_held.pop(index)
        print("Dice on table:", self.state.dice_on_table)
        print("Dice held:", self.state.dice_held)

    def score(self, category: Category):
        self.state.categories[self.state.turn][category] = 0
        self.state.state_type = StateType.END_OF_TURN

    def end_turn(self):
        if self.is_game_finished():
            self.end_game()
        else:
            self.new_turn()

    def new_turn(self):
        self.state.state_type = StateType.INITIAL
        self.state.turn = 1 - self.state.turn
        self.state.rolls_left = 3
        self.state.dice_held = []
        self.state.dice_on_table = [1, 2, 3, 4, 5]
        self.roll()

    def end_game(self):
        self.state.state_type = StateType.FINAL

    def is_game_finished(self) -> bool:
        for category, score in self.state.categories[self.state.turn].items():
            if score == -1:
                return False

    def reset(self):
        self.state.state_type = StateType.INITIAL
        self.state = State()
        self.state.turn = 1
        self.state.score = (0, 0)
        self.state.rolls_left = 3
        self.state.dice_on_table = [1, 2, 3, 4, 5]

    def get_player_choice(self):
        if self.state.state_type == StateType.HOLDING:
            choice = input("Choose action: hold, release, score: ")
        else:
            choice = input("Choose action: hold, release, roll, score: ")
        match choice:
            case "hold":
                index = int(input("Enter index: "))
                self.hold(index)
            case "release":
                index = int(input("Enter index: "))
                self.release(index)
            case "score":
                self.state.state_type = StateType.SCORING
            case "roll":
                if self.state.state_type == StateType.HOLDING:
                    print("Cannot roll with zero rolls left")
                else:
                    self.roll()

    def play(self):
        while self.state.state_type != StateType.FINAL:
            match self.state.state_type:
                case StateType.INITIAL:
                    self.roll()
                case StateType.ROLLING:
                    self.get_player_choice()
                case StateType.HOLDING:
                    self.get_player_choice()
                case StateType.SCORING:
                    print("Categories:", [category.name for category in Category])
                    category = input("Enter category: ")
                    self.score(match_str_to_category(category))
                case StateType.END_OF_TURN:
                    self.end_turn()
                case StateType.FINAL:
                    print("Game over")
                    print("Scores:", self.state.score)
                    print("Winner:", "Player 1" if self.state.score[0] > self.state.score[1] else "Player 2")
                    break


if __name__ == "__main__":
    game = Yahtzee()
    game.play()
