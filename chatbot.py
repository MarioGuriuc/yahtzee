import tkinter as tk
from tkinter import scrolledtext
from openai import OpenAI

from state import State
from utils import serialize_score_for_category, serialize_game_state

client = OpenAI(
	base_url='http://localhost:11434/v1',
	api_key='ollama',
)


class ChatBotApp:
	def __init__(self, root, game_state: State):
		self.root = root
		self.root.title("Yahtzee Helper ChatBot")
		self.game_state = game_state
		self.conversation_history = [
			{"role": "system", "content": "You are a helpful assistant for the game Yahtzee. "
										  "Do not provide answers that are not related to the game Yahtzee, ever. "
										  "If asked about the opponent, do not provide any information about the them. "
										  "If asked who you are, respond with 'I am a Yahtzee assistant.'"
										  "If asked an off-topic question, respond with 'I am a Yahtzee assistant and I can only help with Yahtzee.'"
										  "Use the provided game state and the unscored categories to answer questions. "
										  "Always consider the game state when responding."
										  "Give short responses. Do not provide long answers or explanations."
										  "Use simple and clear language. Do not use jargon or technical terms."
										  "Refer to Player 1 as 'you' and Player 2 as 'the opponent'."}
		]

		self.chat_display = scrolledtext.ScrolledText(
			root, wrap=tk.WORD, state='disabled', width=70, height=25,
			bg="#ffffff", fg="#333333", font=("Arial", 12), padx=10, pady=10
		)
		self.chat_display.grid(row=0, column=0, columnspan=2, padx=15, pady=15)

		self.input_field = tk.Entry(
			root, width=65, font=("Arial", 12), bg="#e6f7ff", fg="#333333", relief=tk.GROOVE
		)
		self.input_field.grid(row=1, column=0, padx=15, pady=10, sticky=tk.W)
		self.input_field.bind("<Return>", lambda event: self.send_message())

		self.send_button = tk.Button(
			root, text="Send", command=self.send_message, bg="#4CAF50", fg="white",
			font=("Arial", 12), width=10, relief=tk.RAISED
		)
		self.send_button.grid(row=1, column=1, padx=15, pady=10, sticky=tk.W)

	def update_game_state(self, serialized_state: str):
		self.conversation_history.append({"role": "user", "content": f"Game State Updated:\n{serialized_state}"})

	def update_score_for_category(self, serialized_score: str):
		self.conversation_history.append(
			{"role": "user", "content": f"Possible score for each unscored category:\n{serialized_score}"})

	def send_message(self):
		user_message = self.input_field.get().strip()
		if user_message:
			self.display_message(f"You: {user_message}")

			self.conversation_history.append({"role": "user", "content": user_message})
			self.conversation_history.append(
				{"role": "user", "content": f"Game State:\n{serialize_game_state(self.game_state)}"})
			self.conversation_history.append({"role": "user",
											  "content": f"Possible score for each unscored category:\n{serialize_score_for_category(self.game_state.dice_on_table)}"})

			bot_response = self.get_bot_response()
			self.display_message(f"Bot: {bot_response}")

			self.input_field.delete(0, tk.END)

	def display_message(self, message):
		self.chat_display.configure(state='normal')
		self.chat_display.insert(tk.END, message + "\n")
		self.chat_display.configure(state='disabled')
		self.chat_display.yview(tk.END)

	def get_bot_response(self):
		try:
			response = client.chat.completions.create(
				model="llama3.2",
				messages=self.conversation_history
			)
			bot_response = response.choices[0].message.content.strip()
			self.conversation_history.append({"role": "assistant", "content": bot_response})
			return bot_response
		except Exception as e:
			return f"Error: {str(e)}"


if __name__ == "__main__":
	root = tk.Tk()
	app = ChatBotApp(root, State())
	root.mainloop()
