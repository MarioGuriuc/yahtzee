import numpy as np
from game import *
from state import *
from state import Category


class QLearningYahtzee(YahtzeeAIBase):
    def __init__(self):
        self.alpha = 0.9  # Learning rate
        self.gamma = 0.95  # Discount factor
        self.epsilon = 1.0  # Exploration probability
        self.epsilon_decay = 0.999999999  # Decay rate
        self.min_epsilon = 0.01  # exploration
        self.q_table = {}  # Q-table

    def get_q_value(self, state: State, action: Action) -> float:
        state_tuple = state.get_state_tuple()
        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = np.zeros(len(Action))
        return self.q_table[state_tuple][action.value]

    def update_q_value(self, state: State, action: Action, reward: float, next_state: State):
        state_tuple = state.get_state_tuple()
        next_state_tuple = next_state.get_state_tuple()

        if state_tuple not in self.q_table:
            self.q_table[state_tuple] = np.zeros(len(Action))
        if next_state_tuple not in self.q_table:
            self.q_table[next_state_tuple] = np.zeros(len(Action))

        max_future_q = np.max(self.q_table[next_state_tuple])
        current_q = self.q_table[state_tuple][action.value]

        self.q_table[state_tuple][action.value] = current_q + self.alpha * (
            reward + self.gamma * max_future_q - current_q
        )

    def decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
    
    def choose_action(self, state: State) -> Action:
        if np.random.rand() < self.epsilon:
            return random.choice(self.get_possible_actions(state))
        else:
            state_tuple = state.get_state_tuple()
            if state_tuple not in self.q_table:
                self.q_table[state_tuple] = np.zeros(len(Action))
            return Action(np.argmax(self.q_table[state_tuple]))
    
    def choose_category(self, state: State) -> Category | None:
        available_categories = [
            (cat, state.calculate_score(cat))
            for cat, score in state.categories[state.turn].items()
            if score == -1
        ]
        if not available_categories:
            return None
        return max(available_categories, key=lambda x: x[1])[0]
    
    def choose_hold(self, state: State) -> list[int]:
        dice_to_hold = []
        for die in state.dice_on_table:
            if die >= 4:
                dice_to_hold.append(die)
            elif np.random.rand() < self.epsilon:
                dice_to_hold.append(die)
        
        return dice_to_hold
    
    def choose_release(self, state: State) -> list[int]:
        dice_to_release = []
        for die in state.dice_held:
            q_value = self.get_q_value(state, Action.RELEASE)
            if np.random.rand() < self.epsilon:
                if np.random.rand() < 0.5:
                    dice_to_release.append(die)
            elif q_value > 0:
                dice_to_release.append(die)
        return dice_to_release




def train_ai(ai: QLearningYahtzee, num_episodes: int, max_turns: int = 13):
    for episode in range(num_episodes):
        game = Yahtzee(ai)
        state = game.state
        total_reward = 0
        consecutive_hold_penalty_count = 0

        for turn in range(max_turns):
            if game.is_game_finished():
                break

            action = ai.choose_action(state)
            reward = 0

            if action == Action.ROLL:
                if state.rolls_left == 0:
                    reward = -20
                else:
                    game.roll()
                    reward = -1
                consecutive_hold_penalty_count = 0

            elif action == Action.HOLD:
                dice_to_hold = ai.choose_hold(state)
                if not dice_to_hold:
                    reward = -10
                else:
                    for die in dice_to_hold:
                        game.hold(state.dice_on_table.index(die))
                    reward = 2 * len(dice_to_hold)

                consecutive_hold_penalty_count += 1
                if consecutive_hold_penalty_count > 1:
                    reward -= 10 * consecutive_hold_penalty_count

            elif action == Action.RELEASE:
                dice_to_release = ai.choose_release(state)
                for die in dice_to_release:
                    game.release(state.dice_held.index(die))
                reward = -2 * len(dice_to_release)
                consecutive_hold_penalty_count = 0

            elif action == Action.SCORE:
                category = ai.choose_category(state)
                if category:
                    reward = game.score(category)
                else:
                    reward = -10
                consecutive_hold_penalty_count = 0

            next_state = game.state
            ai.update_q_value(state, action, reward, next_state)
            total_reward += reward
            state = next_state
            ai.decay_epsilon()

        if episode % 100 == 0:
            print(f"Episode {episode + 1}, Total Reward: {total_reward}, Epsilon: {ai.epsilon:.4f}")

    print("Training complete!")


