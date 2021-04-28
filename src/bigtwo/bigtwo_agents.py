import numpy as np

from src.card_data_structures import Card, UnrecognizedCardException, CardCollection
from src.bigtwo.bigtwo_env import compare_cards, get_smallest_card, compare_plays, get_hand_value


class Agent:
    def __init__(self, name=None, seed=None):
        self.name = name
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
    def __init__(self, name=None, seed=None):
        super().__init__(name, seed)

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


class GreedyAgent(Agent):
    def get_action(self, state):
        poss_moves = state.get_valid_moves()
        if len(poss_moves) == 1:
            return poss_moves[0]

        min_card = None
        filtered_poss_moves = []
        for move in poss_moves:
            if move.num_cards() != 0:
                move_min_card = get_smallest_card(move)
                if min_card is None or compare_cards(min_card, move_min_card) == 1:
                    min_card = move_min_card
                    filtered_poss_moves = []
                if move_min_card == min_card:
                    filtered_poss_moves.append(move)

        candidate = None
        for move in filtered_poss_moves:
            if candidate is None:
                candidate = move
            if state.mode == "any" or state.mode == "fivecard":
                if candidate.num_cards() < move.num_cards():
                    candidate = move
                elif candidate.num_cards() == move.num_cards() and get_hand_value(candidate) > get_hand_value(move):
                    candidate = move
            else:
                if get_hand_value(candidate) > get_hand_value(move):
                    candidate = move

        return candidate