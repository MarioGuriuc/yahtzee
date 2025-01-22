# Yahtzee

This repository contains a digital implementation of the classic Yahtzee dice game, developed in Python. The game features a graphical user interface (GUI) and a helpful AI ChatBot.
# Features

## Graphical User Interface (GUI): Interact with the game through a user-friendly interface.
## AI Chatbot: Utilizes Ollama 3.2 with OpenAI's API to provide in-game assistance and enhance gameplay by offering tips and explanations.
## State-Based Programming: Ensures clear separation of game states for better maintainability and readability.
## Q-Learning for AI: In addition to the chatbot functionality, we implemented Q-learning to enhance the AI's decision-making capabilities. The AI learns optimal strategies for scoring combinations based on rewards for different moves, improving its performance over time. This ensures smarter and more competitive gameplay against the AI.

# Installation

Clone the repository:

    git clone https://github.com/MarioGuriuc/yahtzee.git

Navigate to the project directory:

    cd yahtzee

Install the required dependencies:

    pip install -r requirements.txt

Install Ollama 3.2:

Ollama 3.2 is a lightweight server for integrating language models. To install, access the following page:

    https://ollama.com/download

# Usage

To start the game, run the following command:
    
    python game.py

# Game Rules

Yahtzee is a dice game where the objective is to score points by rolling five dice to make certain combinations. The game consists of 13 rounds, and in each round, you roll the dice and then score the roll in one of 13 categories. You must score once in each category. The score is determined by a different rule for each category. The aim is to maximize your total score.
