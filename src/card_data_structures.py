import random


allowed_ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
allowed_suits = ['C', 'D', 'H', 'S']


class Card:
    def __init__(self, rank, suit):
        suit = suit.upper()

        assert rank in allowed_ranks
        assert suit in allowed_suits

        self.rank = rank
        self.suit = suit

    def parse_card(self, mode="default"):
        if mode == "default":
            r = self.rank
            if r == 1:
                r = 'A'
            elif r == 10:
                r = 'T'
            elif r == 11:
                r = 'J'
            elif r == 12:
                r = 'Q'
            elif r == 13:
                r = 'K'
            return "{}{}".format(r, self.suit)
        else:
            raise Exception("Mode \"{}\" for parsing cards does not exist.".format(mode))

    def __str__(self):
        return self.parse_card(mode="default")

    def __eq__(self, other):
        if isinstance(other, Card):
            if self.rank == other.rank and self.suit == other.suit:
                return True
        return False

    def __hash__(self):
        return hash(str(self))


class CardCollection:
    def __init__(self, cards=None):
        if cards is None:
            self.cards = []
        else:
            self.cards = cards
        self.card_set = set(self.cards)

    def __str__(self):
        return str([str(c) for c in self.cards])

    def num_cards(self):
        return len(self.cards)

    def shuffle(self):
        random.shuffle(self.cards)

    def contains(self, card):
        return card in self.card_set

    def add_top(self, card):
        self.card_set.add(card)
        self.cards.insert(0, card)

    def add_bottom(self, card):
        self.card_set.add(card)
        self.cards.append(card)

    def remove(self, card):
        if card in self.card_set:
            self.card_set.remove(card)
            self.cards.remove(card)
            return True
        return False

    def deal(self, num_piles):
        piles = [[] for _ in range(num_piles)]
        for i in range(len(self.cards)):
            piles[i % num_piles].append(self.cards[i])

        piles = [CardCollection(cards=p) for p in piles]
        return piles

    def __repr__(self):
        return str([str(card) for card in self.cards])


class Deck(CardCollection):
    def __init__(self):
        deck = []
        for suit in allowed_suits:
            for rank in allowed_ranks:
                deck.append(Card(rank, suit))
        super().__init__(deck)
