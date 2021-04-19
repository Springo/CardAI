import numpy as np

from src.card_data_structures import Card, UnrecognizedCardException, CardCollection


class Agent:
    def __init__(self, seed=None):
        self.seed = seed
        if seed is None:
            self.rand_state = np.random.RandomState()
        else:
            self.rand_state = np.random.RandomState(seed)

    def send_initial_state(self, state):
        pass

    def get_action(self, state):
        pass

    def send_feedback(self, state, action, reward, new_state, done):
        pass


class RandomAgent(Agent):
    def get_action(self, state):
        poss_moves = state.get_valid_moves()
        return self.rand_state.choice(poss_moves)


class HumanAgent(Agent):
    def __init__(self, seed=None):
        super().__init__(seed)

        self.allowed_ranks = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
        self.allowed_suits = {'C', 'D', 'H', 'S'}

    def get_action(self, state):
        print("Your hand contains: {}".format(state.hand))

        cards_to_play = []
        played_cards = 0
        command = None
        while command != "END" and command != "PASS" and played_cards < 5:
            command = input("Enter a card to play -> ")
            command = command.upper()
            if command != "END" and command != "PASS":
                try:
                    card = Card.str_to_card(command)
                    cards_to_play.append(card)
                    played_cards += 1
                except UnrecognizedCardException:
                    print("That command is invalid. Please try again.")
        return CardCollection(cards_to_play)
