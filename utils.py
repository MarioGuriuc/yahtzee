import tkinter as tk

from PIL import Image, ImageTk


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
