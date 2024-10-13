import time
import tkinter as tk
from PIL import Image, ImageTk

from game import *
import random


def load_and_resize_image(image_path, size):
    """Helper function to load and resize an image."""
    image = Image.open(image_path)
    resized_image = image.resize(size, Image.DEFAULT_STRATEGY)
    return ImageTk.PhotoImage(resized_image)


def load_dice_image(dice_value, size=(80, 80)):
    dice_names = ["one", "two", "three", "four", "five", "six"]
    image_name = dice_names[dice_value - 1]
    image_path = f"img/dice_{image_name}.png"
    return load_and_resize_image(image_path, size)


class YahtzeeApp:
    def __init__(self, root_param):
        self.game = Yahtzee()
        self.root = root_param
        self.root.title("Yahtzee")
        self.root.geometry("1280x780")
        self.score_labels = {}
        self.ai_score_labels = {}
        self.score_buttons = {}
        self.total_score_labels = {}

        self.canvas = tk.Canvas(self.root, width=1280, height=760)
        self.canvas.pack()

        self.roll_dice_button = tk.Button(self.root, text="Roll Dice", command=self.start_roll_animation)
        self.roll_dice_button.place(x=460, y=430, width=101, height=41)

        self.label_player = tk.Label(self.root, text="You")
        self.label_player.place(x=1093, y=0, width=91, height=41)

        self.label_ai = tk.Label(self.root, text="AI")
        self.label_ai.place(x=1150, y=0, width=91, height=41)

        self.score_frame = tk.Frame(self.root)
        self.score_frame.place(x=980, y=40, width=261, height=740)

        i = 0
        for name, category in categories.items():
            score_frame_row = tk.Frame(self.score_frame, borderwidth=1, relief="solid")
            score_frame_row.grid(row=i, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

            button = tk.Button(score_frame_row, text=name, command=lambda cat=category: self.on_score_push(cat),
                               width=15)
            button.grid(row=0, column=0, padx=5, pady=5)

            self.score_buttons[category] = button

            human_score_label = tk.Label(score_frame_row, text="0")
            human_score_label.grid(row=0, column=1, padx=5, pady=5)
            self.score_labels[category] = human_score_label

            empty_label = tk.Label(score_frame_row, text="", width=3)
            empty_label.grid(row=0, column=2, padx=5, pady=5)
            ai_score_label = tk.Label(score_frame_row, text="0")
            ai_score_label.grid(row=0, column=3, padx=5, pady=5)
            self.ai_score_labels[category] = ai_score_label
            i += 1

        score_frame_row = tk.Frame(self.score_frame, borderwidth=1, relief="solid")
        score_frame_row.grid(row=i, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        total_score_button = tk.Button(score_frame_row, text="Total Score", width=15)
        total_score_button.grid(row=0, column=0, padx=5, pady=5)
        self.total_score_labels[0] = human_score_label = tk.Label(score_frame_row, text="0")
        human_score_label.grid(row=0, column=1, padx=5, pady=5)
        empty_label = tk.Label(score_frame_row, text="", width=3)
        empty_label.grid(row=0, column=2, padx=5, pady=5)
        self.total_score_labels[1] = ai_score_label = tk.Label(score_frame_row, text="0")
        ai_score_label.grid(row=0, column=3, padx=5, pady=5)

        self.dice_positions_on_table = [(240, 330), (350, 330), (470, 330), (590, 330), (710, 330)]
        self.dice_positions_hold_human = [(240, 500), (350, 500), (470, 500), (590, 500), (710, 500)]
        self.dice_positions_hold_ai = [(240, 150), (350, 150), (470, 150), (590, 150), (710, 150)]
        self.dice_images = []

        for i in range(5):
            dice_image = load_dice_image(i, size=(80, 80))
            self.dice_images.append(dice_image)
            x, y = self.dice_positions_on_table[i]

            dice_id = self.canvas.create_image(x, y, image=dice_image, anchor=tk.NW)
            self.canvas.tag_bind(dice_id)

        self.rolls_left_label = tk.Label(self.root, text=f"Rolls Left: {self.game.state.rolls_left}")
        self.rolls_left_label.place(x=440, y=480, width=150, height=10)

        self.ai_action_label = tk.Label(self.root, font=("Arial", 12))
        self.ai_action_label.place(x=580, y=50, width=400, height=20)

        self.human_photo = load_and_resize_image("img/human_photo.png", (100, 100))
        self.canvas.create_image(460, 670, image=self.human_photo, anchor=tk.NW)

        self.ai_photo = load_and_resize_image("img/ai_photo.png", (100, 100))
        self.canvas.create_image(460, 10, image=self.ai_photo, anchor=tk.NW)

    def draw_dice(self):
        self.dice_images.clear()
        self.game.state.dice_on_table = sorted(self.game.state.dice_on_table)
        for i, value in enumerate(self.game.state.dice_on_table):
            dice_image = load_dice_image(value, size=(80, 80))
            self.dice_images.append(dice_image)
            x, y = self.dice_positions_on_table[i]

            dice_id = self.canvas.create_image(x, y, image=dice_image, anchor=tk.NW)
            self.canvas.tag_bind(dice_id, "<Button-1>", lambda event, idx=i: self.toggle_dice_hold(idx))

        self.game.state.dice_held = sorted(self.game.state.dice_held)
        for i, value in enumerate(self.game.state.dice_held):
            dice_image = load_dice_image(value, size=(80, 80))
            self.dice_images.append(dice_image)
            x, y = self.dice_positions_hold_human[i] if self.game.state.turn == 0 else self.dice_positions_hold_ai[i]
            dice_id = self.canvas.create_image(x, y, image=dice_image, anchor=tk.NW)
            self.canvas.tag_bind(dice_id, "<Button-1>", lambda event, idx=i: self.toggle_dice_release(idx))

    def start_roll_animation(self):
        if self.game.state.rolls_left == 0:
            return
        self.roll_dice_button.config(state=tk.DISABLED)
        roll_duration = 1000
        roll_interval = 50
        end_time = time.time() + roll_duration / 1000

        def roll_step():
            if time.time() < end_time:
                for i in range(len(self.game.state.dice_on_table)):
                    random_value = random.randint(1, 6)
                    dice_image = load_dice_image(random_value, size=(80, 80))
                    self.canvas.create_image(self.dice_positions_on_table[i], image=dice_image, anchor=tk.NW)
                    self.dice_images.append(dice_image)
                self.root.after(roll_interval, roll_step)
            else:
                self.roll_dice()
                if self.game.state.turn == 1:
                    self.root.after(1000, self.ai_action)

        roll_step()

    def roll_dice(self):
        if self.game.state.rolls_left > 0 and len(self.game.state.dice_held) < 5:
            self.ai_action_label.config(text="")
            self.game.roll()
            self.draw_dice()
            self.update_possible_score_labels()
            self.update_rolls_left_label()
        self.roll_dice_button.config(state=tk.NORMAL)

    def toggle_dice_hold(self, index):
        if index < len(self.game.state.dice_on_table) and self.game.state.turn == 0:
            dice_value = self.game.state.dice_on_table.pop(index)
            self.game.state.dice_held.append(dice_value)
            self.draw_dice()

    def toggle_dice_release(self, index):
        if index < len(self.game.state.dice_held) and self.game.state.turn == 0:
            dice_value = self.game.state.dice_held.pop(index)
            self.game.state.dice_on_table.append(dice_value)
            self.draw_dice()

    def on_score_push(self, category):
        if (self.game.state.categories[self.game.state.turn][category] == -1
                and self.game.state.state_type != StateType.INITIAL):
            self.game.score(category)
            self.update_score_label(category, self.game.state.categories[self.game.state.turn][category])
            self.end_turn()
            self.ai_action()
            self.score_buttons[category].config(state=tk.DISABLED, bg="lightgray")

    def update_score_label(self, category, score):
        if self.game.state.turn == 0:
            self.score_labels[category].config(text=str(score), fg="red")
        else:
            self.ai_score_labels[category].config(text=str(score), fg="red")
        for cat in self.game.state.categories[0]:
            if self.score_labels[cat].cget("fg") == "green":
                self.score_labels[cat].config(fg="black", text="0")
            if self.ai_score_labels[cat].cget("fg") == "green":
                self.ai_score_labels[cat].config(fg="black", text="0")
        self.total_score_labels[0].config(text=str(self.game.state.score[0]))
        self.total_score_labels[1].config(text=str(self.game.state.score[1]))

    def update_possible_score_labels(self):
        for category in self.game.state.categories[0]:
            if self.game.state.categories[self.game.state.turn][category] == -1:
                score = self.game.ai.simulate_score(category, self.game.state)
                self.score_labels[category].config(text=str(score), fg="green") if self.game.state.turn == 0 else \
                    self.ai_score_labels[category].config(text=str(score), fg="green")

    def update_rolls_left_label(self):
        self.rolls_left_label.config(text=f"Rolls Left: {self.game.state.rolls_left}")

    def ai_action(self):
        action = self.game.ai.choose_action(self.game.state)

        if action == "score":
            category = self.game.ai.choose_category(self.game.state)
            if category:
                self.update_ai_action_label(self.game.score(category))
                self.update_score_label(category, self.game.state.categories[self.game.state.turn][category])
            self.end_turn()
            self.update_rolls_left_label()
        elif action == "roll":
            self.root.after(1000, self.ai_roll_dice)
        elif action == "hold":
            self.root.after(1000, self.ai_hold_dice)

    def ai_roll_dice(self):
        self.start_roll_animation()

    def ai_hold_dice(self):
        dice_to_hold = self.game.ai.choose_hold(self.game.state.dice_on_table)

        def hold_dice_with_delay(index):
            if index < len(dice_to_hold):
                die = dice_to_hold[index]
                die_index = self.game.state.dice_on_table.index(die)
                self.game.hold(die_index)
                self.draw_dice()
                self.root.after(1000, hold_dice_with_delay, index + 1)

        hold_dice_with_delay(0)
        self.root.after(len(dice_to_hold) * 1000 + 1000, self.ai_action)

    def end_turn(self):
        self.game.end_turn()
        self.draw_dice()
        if self.game.state.state_type == StateType.FINAL:
            winner = "AI" if self.game.state.score[1] > self.game.state.score[0] else "You"
            winner_label = tk.Label(self.root, text=f"{winner} won!", font=("Arial", 12))
            winner_label.place(x=310, y=300, width=400, height=20)
            play_again_button = tk.Button(self.root, text="Play Again", command=self.reset_game)
            play_again_button.place(x=460, y=430, width=101, height=41)

    def update_ai_action_label(self, param):
        self.ai_action_label.config(text="AI" + param)

    def reset_game(self):
        self.game.reset()
        self.draw_dice()
        for category in categories.keys():
            self.score_labels[categories[category]].config(text="0", fg="black")
            self.ai_score_labels[categories[category]].config(text="0", fg="black")
            self.score_buttons[categories[category]].config(state=tk.NORMAL)
        self.total_score_labels[0].config(text="0")
        self.total_score_labels[1].config(text="0")
        self.update_rolls_left_label()
        self.ai_action_label.config(text="")
        self.roll_dice_button.config(state=tk.NORMAL)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "Play Again" \
                    or isinstance(widget, tk.Label) and widget.cget("text") == "AI won!" \
                    or isinstance(widget, tk.Label) and widget.cget("text") == "You won!":
                widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = YahtzeeApp(root)
    root.mainloop()
