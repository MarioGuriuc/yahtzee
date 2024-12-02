import os
import time

from constants import *
from game import *
from utils import *
from q_learning import *


class YahtzeeApp:
	def __init__(self, root_param: tk.Tk, game: Yahtzee):
		self.game = game
		self.root = root_param
		self.root.title("Yahtzee")
		self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
		self.score_labels = {}
		self.ai_score_labels = {}
		self.score_buttons = {}
		self.total_score_labels = {}
		self.ai_photo = None
		self.human_photo = None

		self.canvas = tk.Canvas(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
		self.canvas.pack()

		self.roll_dice_button = create_new_button(self.root, "Roll Dice", self.start_roll_animation, ROLL_BUTTON_X,
												  ROLL_BUTTON_Y, ROLL_BUTTON_WIDTH, ROLL_BUTTON_HEIGHT)

		self.label_player = create_new_label(self.root, "You",
											 PLAYER_LABEL_X, PLAYER_LABEL_Y, 91, 41)

		self.label_ai = create_new_label(self.root, "AI",
										 AI_LABEL_X, AI_LABEL_Y, 91, 41)

		self.score_frame = tk.Frame(self.root)
		self.score_frame.place(x=980, y=40, width=261, height=740)

		self.setup_score_frame()
		self.dice_images = []

		self.draw_initial_dice()

		self.load_player_ai_photos()

		self.rolls_left_label = create_new_label(self.root, "Rolls Left: 3",
												 ROLLS_LEFT_LABEL_X, ROLLS_LEFT_LABEL_Y, 150, 10)

		self.ai_action_label = create_new_label(self.root, "",
												AI_ACTION_LABEL_X, AI_ACTION_LABEL_Y, 400, 20)

		self.load_player_ai_photos()

	"""GUI"""

	def draw_initial_dice(self) -> None:
		for i in range(5):
			dice_image = load_dice_image(i, size=(80, 80))
			self.dice_images.append(dice_image)
			x, y = DICE_POSITIONS_ON_TABLE[i]
			dice_id = self.canvas.create_image(x, y, image=dice_image, anchor=tk.NW)
			self.canvas.tag_bind(dice_id)

	def load_player_ai_photos(self) -> None:
		self.human_photo = load_and_resize_image(HUMAN_IMAGE_PATH, (100, 100))
		self.canvas.create_image(460, 670, image=self.human_photo, anchor=tk.NW)

		self.ai_photo = load_and_resize_image(AI_IMAGE_PATH, (100, 100))
		self.canvas.create_image(460, 10, image=self.ai_photo, anchor=tk.NW)

	def create_score_row(self, row_idx: int, name: str, category: Category) -> None:
		score_frame_row = tk.Frame(self.score_frame, borderwidth=1, relief="solid")
		score_frame_row.grid(row=row_idx, column=0, columnspan=3, padx=5, pady=5, sticky='ew')

		button = tk.Button(score_frame_row, text=name, command=lambda cat=category: self.on_score_push(cat), width=15)
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

	def create_total_score_row(self) -> None:
		score_frame_row = tk.Frame(self.score_frame, borderwidth=1, relief="solid")
		score_frame_row.grid(row=len(categories), column=0, columnspan=3, padx=5, pady=5, sticky='ew')

		total_score_button = tk.Button(score_frame_row, text="Total Score", width=15)
		total_score_button.grid(row=0, column=0, padx=5, pady=5)

		self.total_score_labels[0] = human_score_label = tk.Label(score_frame_row, text="0")
		human_score_label.grid(row=0, column=1, padx=5, pady=5)

		empty_label = tk.Label(score_frame_row, text="", width=3)
		empty_label.grid(row=0, column=2, padx=5, pady=5)

		self.total_score_labels[1] = ai_score_label = tk.Label(score_frame_row, text="0")
		ai_score_label.grid(row=0, column=3, padx=5, pady=5)

	def setup_score_frame(self) -> None:
		self.score_frame = tk.Frame(self.root)
		self.score_frame.place(x=SCORE_FRAME_X, y=SCORE_FRAME_Y, width=SCORE_FRAME_WIDTH, height=SCORE_FRAME_HEIGHT)

		for i, (name, category) in enumerate(categories.items()):
			self.create_score_row(i, name, category)

		self.create_total_score_row()

	def draw_dice(self) -> None:
		self.dice_images.clear()
		self.game.state.dice_on_table = sorted(self.game.state.dice_on_table)
		for i, value in enumerate(self.game.state.dice_on_table):
			dice_image = load_dice_image(value, size=DICE_IMAGE_SIZE)
			self.dice_images.append(dice_image)
			x, y = DICE_POSITIONS_ON_TABLE[i]

			dice_id = self.canvas.create_image(x, y, image=dice_image, anchor=tk.NW)
			self.canvas.tag_bind(dice_id, "<Button-1>", lambda event, idx=i: self.toggle_dice_hold(idx))

		self.game.state.dice_held = sorted(self.game.state.dice_held)
		for i, value in enumerate(self.game.state.dice_held):
			dice_image = load_dice_image(value, size=DICE_IMAGE_SIZE)
			self.dice_images.append(dice_image)
			x, y = DICE_POSITIONS_HOLD_HUMAN[i] if self.game.state.turn == 0 else DICE_POSITIONS_HOLD_AI[i]
			dice_id = self.canvas.create_image(x, y, image=dice_image, anchor=tk.NW)
			self.canvas.tag_bind(dice_id, "<Button-1>", lambda event, idx=i: self.toggle_dice_release(idx))

	"""GUI"""

	def start_roll_animation(self) -> None:
		if self.game.state.rolls_left > 0:
			self.roll_dice_button.config(state=tk.DISABLED) if self.game.state.turn == 0 else None
			end_time = time.time() + 1

			def roll_step():
				if time.time() < end_time:
					for i in range(len(self.game.state.dice_on_table)):
						random_value = random.randint(1, 6)
						dice_image = load_dice_image(random_value, DICE_IMAGE_SIZE)
						self.canvas.create_image(DICE_POSITIONS_ON_TABLE[i], image=dice_image, anchor=tk.NW)
						self.dice_images.append(dice_image)
					self.root.after(DICE_ROLL_INTERVAL, roll_step)
				else:
					self.roll_dice()
					if self.game.state.turn == 1:
						self.root.after(DICE_ROLL_DURATION, self.ai_action)

			roll_step()

	def roll_dice(self) -> None:
		if self.game.state.rolls_left > 0 and len(self.game.state.dice_held) < 5:
			self.ai_action_label.config(text="")
			self.game.roll()
			self.draw_dice()
			self.update_possible_score_labels()
			self.update_rolls_left_label()
			self.roll_dice_button.config(state=tk.NORMAL) if self.game.state.turn == 0 else None

	def toggle_dice_hold(self, dice_index: int) -> None:
		if dice_index < len(
				self.game.state.dice_on_table) and self.game.state.turn == 0 and self.game.state.state_type != StateType.INITIAL:
			dice_value = self.game.state.dice_on_table.pop(dice_index)
			self.game.state.dice_held.append(dice_value)
			self.draw_dice()

	def toggle_dice_release(self, dice_index: int) -> None:
		if dice_index < len(self.game.state.dice_held) and self.game.state.turn == 0:
			dice_value = self.game.state.dice_held.pop(dice_index)
			self.game.state.dice_on_table.append(dice_value)
			self.draw_dice()

	def on_score_push(self, category) -> None:
		if (self.game.state.categories[self.game.state.turn][category] == -1
				and self.game.state.state_type != StateType.INITIAL and self.game.state.turn == 0):
			self.roll_dice_button.config(state=tk.DISABLED)
			score = self.game.score(category)
			self.update_score_label(category, score)
			self.end_turn()
			self.ai_action()
			self.score_buttons[category].config(state=tk.DISABLED, bg="lightgray")

	def update_score_label(self, category, score) -> None:
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

	def update_possible_score_labels(self) -> None:
		for category in self.game.state.categories[0]:
			if self.game.state.categories[self.game.state.turn][category] == -1:
				score = self.game.calculate_score(category)
				self.score_labels[category].config(text=str(score), fg="green") if self.game.state.turn == 0 else \
					self.ai_score_labels[category].config(text=str(score), fg="green")

	def update_rolls_left_label(self) -> None:
		self.rolls_left_label.config(text=f"Rolls Left: {self.game.state.rolls_left}")

	def ai_action(self) -> None:
		action = self.game.ai.choose_action(self.game.state)
		print(action)
		match action:
			case Action.ROLL:
				self.root.after(DICE_ROLL_DURATION, self.start_roll_animation)
			case Action.SCORE:
				self.ai_score()
			case Action.HOLD:
				self.ai_hold_dice()
			case Action.RELEASE:
				self.ai_release_dice()

	def ai_score(self):
		self.roll_dice_button.config(state=tk.NORMAL)
		category = self.game.ai.choose_category(self.game.state)
		score = self.game.score(category)
		self.ai_action_label.config(text=f"AI scored {str(score)} in {category.name}!")
		self.update_score_label(category, score)
		self.end_turn()
		self.update_rolls_left_label()

	def ai_release_dice(self) -> None:
		dice_to_release = self.game.ai.choose_release(self.game.state)

		def release_dice_with_delay(index):
			if index < len(dice_to_release):
				die = dice_to_release[index]
				die_index = self.game.state.dice_held.index(die)
				self.game.release(die_index)
				self.draw_dice()
				self.root.after(DICE_HOLD_DURATION, release_dice_with_delay, index + 1)

		release_dice_with_delay(0)
		self.root.after(len(dice_to_release) * DICE_HOLD_DURATION + DICE_HOLD_DURATION, self.ai_action)

	def ai_hold_dice(self) -> None:
		dice_to_hold = self.game.ai.choose_hold(self.game.state)

		def hold_dice_with_delay(index):
			if index < len(dice_to_hold):
				die = dice_to_hold[index]
				die_index = self.game.state.dice_on_table.index(die)
				self.game.hold(die_index)
				self.draw_dice()
				self.root.after(DICE_HOLD_DURATION, hold_dice_with_delay, index + 1)

		hold_dice_with_delay(0)
		self.root.after(len(dice_to_hold) * DICE_HOLD_DURATION + DICE_HOLD_DURATION, self.ai_action)

	def end_turn(self) -> None:
		if self.game.is_game_finished():
			winner = "AI" if self.game.state.score[1] > self.game.state.score[0] else "You"
			create_new_label(self.root, f"{winner} won!", 460, 430, 101, 41)
			create_new_button(self.root, "Play Again", self.reset_game, 460, 480, 101, 41)
		else:
			self.game.end_turn()
			self.update_rolls_left_label()
			self.draw_dice()

	def reset_game(self) -> None:
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
	# ai = RandomYahtzeeAI()
	ai = QLearningYahtzee()
	if not os.path.exists(ai.q_table_file):
		print("Training AI...")
		train_ai(ai, num_episodes=1000, max_turns=24, num_threads=4)
		ai.save_q_table()
	else:
		print("Q-table loaded. Skipping training.")
	app = YahtzeeApp(root, Yahtzee(ai))
	root.mainloop()
