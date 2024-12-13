import tkinter as tk
from PIL import Image, ImageTk
from game import Category

def load_and_resize_image(image_path, size):
    image = Image.open(image_path)
    resized_image = image.resize(size, Image.DEFAULT_STRATEGY)
    return ImageTk.PhotoImage(resized_image)

def load_dice_image(dice_value, size=(80, 80)):
    dice_names = ["one", "two", "three", "four", "five", "six"]
    image_name = dice_names[dice_value - 1]
    image_path = f"img/dice_{image_name}.png"
    return load_and_resize_image(image_path, size)

def create_new_button(root, text, command, x, y, width, height):
    button = tk.Button(root, text=text, command=command)
    button.place(x=x, y=y, width=width, height=height)
    return button

def create_new_label(root, text, x, y, width, height):
    label = tk.Label(root, text=text)
    label.place(x=x, y=y, width=width, height=height)
    return label

def calculate_score(category: Category, dice: list) -> int:
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

def calculate_probability(category: Category, current_dice: list, remaining_rolls: int) -> float:
    dice_counts = {i: current_dice.count(i) for i in range(1, 7)}
    total_dice = len(current_dice)

    if category == Category.YAHTZEE:
        max_count = max(dice_counts.values())
        needed = 5 - max_count
        if needed <= 0:
            return 1.0
        elif needed > remaining_rolls:
            return 0.0
        else:
            return (1 / 6) ** needed

    elif category == Category.FULL_HOUSE:
        if sorted(dice_counts.values()) == [2, 3]:
            return 1.0
        if remaining_rolls == 0:
            return 0.0
        pairs = sum(1 for count in dice_counts.values() if count >= 2)
        triples = sum(1 for count in dice_counts.values() if count >= 3)
        return 0.2 * pairs + 0.3 * triples

    elif category == Category.THREE_OF_A_KIND:
        max_count = max(dice_counts.values())
        needed = 3 - max_count
        if needed <= 0:
            return 1.0
        elif needed > remaining_rolls:
            return 0.0
        else:
            return 1 - ((5 - total_dice) / 6) ** needed

    elif category == Category.FOUR_OF_A_KIND:
        max_count = max(dice_counts.values())
        needed = 4 - max_count
        if needed <= 0:
            return 1.0 
        elif needed > remaining_rolls:
            return 0.0
        else:
            return 1 - ((5 - total_dice) / 6) ** needed

    elif category == Category.SMALL_STRAIGHT:
        small_straight_patterns = [
            {1, 2, 3, 4},
            {2, 3, 4, 5},
            {3, 4, 5, 6}
        ]
        current_set = set(current_dice)
        for pattern in small_straight_patterns:
            if pattern.issubset(current_set):
                return 1.0
        if remaining_rolls == 0:
            return 0.0
        return 0.5

    elif category == Category.LARGE_STRAIGHT:
        large_straight_patterns = [
            {1, 2, 3, 4, 5},
            {2, 3, 4, 5, 6}
        ]
        current_set = set(current_dice)
        for pattern in large_straight_patterns:
            if pattern.issubset(current_set):
                return 1.0
        if remaining_rolls == 0:
            return 0.0
        return 0.3

    elif category == Category.CHANCE:
        return 0.1

    else:
        return 0.0
