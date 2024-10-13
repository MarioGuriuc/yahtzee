from state import *
import random


def match_str_to_category(category: str) -> Category:
    return categories[category]


class YahtzeeAI:
    def __init__(self):
        pass

    def choose_action(self, state: State) -> str:
        if state.state_type == StateType.INITIAL:
            return "roll"
        if state.rolls_left == 0 or len(state.dice_on_table) == 0:
            return "score"

        if self.is_good_hold(state):
            return "hold"

        if self.should_score(state):
            return "score"

        return "roll"

    def choose_category(self, state):
        available_categories = []

        for category, score in state.categories[state.turn].items():
            if score == -1:
                available_categories.append(category)

        best_category = None
        best_score = -1

        for category in available_categories:
            simulated_score = self.simulate_score(category, state)
            if simulated_score > best_score:
                best_score = simulated_score
                best_category = category

        return best_category if best_category is not None else None

    def choose_hold(self, dice_on_table: list[int]) -> list[int]:
        counts = {i: dice_on_table.count(i) for i in range(1, 7)}
        best_dice_to_hold = []

        for die, count in counts.items():
            if count >= 2:
                best_dice_to_hold += [die] * count

        if not best_dice_to_hold:
            best_dice_to_hold = sorted(dice_on_table, reverse=True)[:2]

        return best_dice_to_hold

    def is_good_hold(self, state: State) -> bool:
        dice = state.dice_on_table
        return self.evaluate_dice_for_holding(dice)

    def should_score(self, state: State) -> bool:
        dice = state.dice_on_table + state.dice_held
        return self.evaluate_dice_for_scoring(dice)

    def evaluate_dice_for_holding(self, dice: list[int]) -> bool:
        counts = {i: dice.count(i) for i in range(1, 7)}

        if any(count >= 2 for count in counts.values()):
            return True

        if sorted([counts[x] for x in set(dice)]) == [2, 3]:
            return True

        if self.potential_straight(dice):
            return True

        return False

    def evaluate_dice_for_scoring(self, dice: list[int]) -> bool:
        counts = {i: dice.count(i) for i in range(1, 7)}

        if any(count >= 3 for count in counts.values()):
            return True

        if sorted([counts[x] for x in set(dice)]) == [2, 3]:
            return True

        if sum(dice) >= 20:
            return True

        return False

    def potential_straight(self, dice):
        unique_dice = list(set(dice))
        unique_dice.sort()

        small_straights = [
            [1, 2, 3, 4],
            [2, 3, 4, 5],
            [3, 4, 5, 6]
        ]
        large_straights = [
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6]
        ]

        for straight in small_straights:
            if all(num in unique_dice for num in straight):
                return True

        for straight in large_straights:
            if all(num in unique_dice for num in straight):
                return True

        return False

    def simulate_score(self, category: Category, state: State) -> int:
        dice = state.dice_on_table + state.dice_held
        score = 0

        match category:
            case Category.ONES:
                score = dice.count(1)
            case Category.TWOS:
                score = dice.count(2) * 2
            case Category.THREES:
                score = dice.count(3) * 3
            case Category.FOURS:
                score = dice.count(4) * 4
            case Category.FIVES:
                score = dice.count(5) * 5
            case Category.SIXES:
                score = dice.count(6) * 6
            case Category.THREE_OF_A_KIND:
                if any(dice.count(x) >= 3 for x in set(dice)):
                    score = sum(dice)
            case Category.FOUR_OF_A_KIND:
                if any(dice.count(x) >= 4 for x in set(dice)):
                    score = sum(dice)
            case Category.FULL_HOUSE:
                if sorted([dice.count(x) for x in set(dice)]) == [2, 3]:
                    score = 25
            case Category.SMALL_STRAIGHT:
                if (len(set(dice) & {1, 2, 3, 4}) == 4 or
                        len(set(dice) & {2, 3, 4, 5}) == 4 or
                        len(set(dice) & {3, 4, 5, 6}) == 4):
                    score = 30
            case Category.LARGE_STRAIGHT:
                if set(dice) == {1, 2, 3, 4, 5} or set(dice) == {2, 3, 4, 5, 6}:
                    score = 40
            case Category.YAHTZEE:
                if len(set(dice)) == 1:
                    score = 50
            case Category.CHANCE:
                score = sum(dice)

        return score


class Yahtzee:
    def __init__(self):
        self.state = State()
        self.ai = YahtzeeAI()

    def roll(self):
        self.state.state_type = StateType.ROLLING
        self.state.rolls_left -= 1
        self.state.dice_on_table = [random.randint(1, 6) for _ in
                                    range(len(self.state.dice_on_table) if self.state.dice_on_table else 5)]
        if self.state.rolls_left == 0:
            self.state.state_type = StateType.HOLDING

    def hold(self, index: int):
        self.state.dice_held.append(self.state.dice_on_table[index])
        self.state.dice_on_table.pop(index)

    def release(self, index: int):
        self.state.dice_on_table.append(self.state.dice_held[index])
        self.state.dice_held.pop(index)

    def score(self, category: Category):
        if self.state.categories[self.state.turn][category] != -1:
            return

        dice = self.state.dice_on_table + self.state.dice_held
        score = 0

        match category:
            case Category.ONES:
                score = dice.count(1) * 1
            case Category.TWOS:
                score = dice.count(2) * 2
            case Category.THREES:
                score = dice.count(3) * 3
            case Category.FOURS:
                score = dice.count(4) * 4
            case Category.FIVES:
                score = dice.count(5) * 5
            case Category.SIXES:
                score = dice.count(6) * 6
            case Category.THREE_OF_A_KIND:
                if any(dice.count(x) >= 3 for x in set(dice)):
                    score = sum(dice)
            case Category.FOUR_OF_A_KIND:
                if any(dice.count(x) >= 4 for x in set(dice)):
                    score = sum(dice)
            case Category.FULL_HOUSE:
                if sorted([dice.count(x) for x in set(dice)]) == [2, 3]:
                    score = 25
            case Category.SMALL_STRAIGHT:
                if (len(set(dice) & {1, 2, 3, 4}) == 4 or
                        len(set(dice) & {2, 3, 4, 5}) == 4 or
                        len(set(dice) & {3, 4, 5, 6}) == 4):
                    score = 30
            case Category.LARGE_STRAIGHT:
                if set(dice) == {1, 2, 3, 4, 5} or set(dice) == {2, 3, 4, 5, 6}:
                    score = 40
            case Category.YAHTZEE:
                if len(set(dice)) == 1:
                    score = 50
            case Category.CHANCE:
                score = sum(dice)

        self.state.categories[self.state.turn][category] = score
        self.state.score[self.state.turn] += score
        self.state.state_type = StateType.END_OF_TURN
        return f" scored {score} in category {category.name}"

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

    def end_game(self):
        self.state.state_type = StateType.FINAL

    def is_game_finished(self) -> bool:
        for category, score in self.state.categories[1 - self.state.turn].items():
            if score == -1:
                return False
        return True

    def reset(self):
        self.state.state_type = StateType.INITIAL
        self.state = State()
        self.state.turn = 0
        self.state.score = {0: 0, 1: 0}
        self.state.rolls_left = 3
        self.state.dice_on_table = [1, 2, 3, 4, 5]
