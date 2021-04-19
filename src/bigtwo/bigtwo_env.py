from src.card_data_structures import Card, CardCollection, Deck

suit_vals = {'C': 0, 'D': 1, 'H': 2, 'S': 3}


def get_card_value(card):
    return ((card.rank - 3) % 13) * 10 + suit_vals[card.suit]


def compare_cards(c1, c2):
    c1_val = get_card_value(c1)
    c2_val = get_card_value(c2)
    if c1_val > c2_val:
        return 1
    if c1_val < c2_val:
        return -1
    return 0


def get_largest_card(cards):
    return max(cards.cards, key=get_card_value)


def sort_cards(cards):
    new_cards = sorted(cards.cards, key=get_card_value)
    return CardCollection(new_cards)


def identify_play(cards):
    n = cards.num_cards()
    cards = sort_cards(cards)
    ranks = [card.rank for card in cards.cards]
    suits = sorted([card.suit for card in cards.cards])
    if n == 0:
        return "pass", None
    elif n == 1:
        return "single", cards.cards[0]
    elif n == 2:
        if ranks[0] == ranks[1]:
            return "double", cards.cards[1]
    elif n == 3:
        if ranks[0] == ranks[2]:
            return "triple", cards.cards[2]
    elif n == 4:
        if ranks[0] == ranks[3]:
            return "quad", cards.cards[3]
    elif n == 5:
        straight = False
        flush = False
        if (ranks[0] == ranks[1] - 1 and ranks[1] == ranks[2] - 1
                and ranks[2] == ranks[3] - 1 and ranks[3] == ranks[4] - 1):
            straight = True
        if suits[0] == suits[4]:
            flush = True
        if straight and flush:
            return "straightflush", cards.cards[4]
        if straight:
            return "straight", cards.cards[4]
        if flush:
            return "flush", cards.cards[4]

        if ranks[0] == ranks[3]:
            return "bomb", cards.cards[3]
        if ranks[1] == ranks[4]:
            return "bomb", cards.cards[4]

        if ranks[0] == ranks[2]:
            return "fullhouse", cards.cards[2]
        if ranks[2] == ranks[4]:
            return "fullhouse", cards.cards[4]

    return "unknown", cards.cards[n - 1]


class BigTwoEnv:
    def __init__(self, num_players=4):
        self.num_players = num_players
        self.player_cards = None
        self.history = None
        self.player_card_count = None
        self.turn = None
        self.mode = None

    def reset(self):
        deck = Deck()
        deck.shuffle()
        self.player_cards = [sort_cards(hand) for hand in deck.deal(self.num_players)]
        self.player_card_count = [pc.num_cards() for pc in self.player_cards]
        self.history = []
        self.mode = "any"

        for i in range(len(self.player_cards)):
            if self.player_cards[i].contains(Card(3, 'C')):
                self.turn = i

        return self.get_state()

    def get_state(self):
        return BigTwoState(self.turn, self.player_cards[self.turn], self.player_card_count, self.history, self.mode)


class BigTwoState:
    def __init__(self, turn, hand, player_card_count, history, mode):
        self.turn = turn
        self.hand = hand
        self.player_card_count = player_card_count
        self.history = history
        self.mode = mode

    def get_valid_moves(self):
        last_move = []
        i = 1
        done = False
        while not done:
            if self.history[-i] == 0:
                done = True
            last_move.append(self.history[-i])


if __name__ == "__main__":
    new_env = BigTwoEnv()
    state = new_env.reset()
    cards = [Card(9, 'S'), Card(10, 'S'), Card(8, 'S'), Card(11, 'S'), Card(5, 'S')]
    hand = CardCollection(cards)
    play, rep_card = identify_play(hand)
    print("{}, {}".format(play, rep_card))
