import random
from itertools import combinations

from src.card_data_structures import Card, CardCollection, Deck

suit_vals = {'C': 0, 'D': 1, 'H': 2, 'S': 3}
hand_vals = {'straight': 0, 'flush': 1, 'fullhouse': 2, 'bomb': 3, 'straightflush': 4}


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
        rep_straight = cards.cards[4]
        if (ranks[0] == ranks[1] - 1 and ranks[1] == ranks[2] - 1
                and ranks[2] == ranks[3] - 1 and ranks[3] == ranks[4] - 1):
            straight = True
        if ranks[3] == 1 and ranks[4] == 2 and ranks[0] == 11 and ranks[1] == 12 and ranks[2] == 13:
            straight = True
        if ranks[4] == 1 and ranks[0] == 10 and ranks[1] == 11 and ranks[2] == 12 and ranks[3] == 13:
            straight = True
        if ranks[3] == 1 and ranks[4] == 2 and ranks[0] == 3 and ranks[1] == 4 and ranks[2] == 5:
            straight = True
            rep_straight = cards.cards[2]
        if ranks[4] == 2 and ranks[0] == 3 and ranks[1] == 4 and ranks[2] == 5 and ranks[3] == 6:
            straight = True
            rep_straight = cards.cards[3]
        if suits[0] == suits[4]:
            flush = True
        if straight and flush:
            return "straightflush", rep_straight
        if straight:
            return "straight", rep_straight
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


def compare_plays(h1, h2):
    p1, p1_rep = identify_play(h1)
    p2, p2_rep = identify_play(h2)
    if p1 == "unknown":
        raise InvalidComparisonException("Play {} could not be identified.".format(h1))
    if p2 == "unknown":
        raise InvalidComparisonException("Play {} could not be identified.".format(h2))

    if p1 != p2 and p1 not in hand_vals and p2 not in hand_vals:
        print("Trying to compare {} with {}".format(p1, p2))

    if p1 == p2:
        if p1 == "straightflush" and p2 == "straightflush":
            if suit_vals[p1_rep] > suit_vals[p2_rep]:
                return 1
            elif suit_vals[p1_rep] < suit_vals[p2_rep]:
                return -1
        return compare_cards(p1_rep, p2_rep)
    elif p2 not in hand_vals or hand_vals[p1] > hand_vals[p2]:
        return 1
    elif p1 not in hand_vals or hand_vals[p1] < hand_vals[p2]:
        return -1
    else:
        raise InvalidComparisonException("Comparison failed all checks.")


def search_plays(hand, type):
    def _collection_combination(iterable, num):
        return [CardCollection(list(hand)) for hand in combinations(iterable, num)]

    def _enumerate_multiples(hand, num):
        plays = []
        cur_rank = None
        start_ind = 0
        counter = 0
        for i in range(hand.num_cards()):
            if hand.cards[i].rank == cur_rank:
                counter += 1
            else:
                if counter >= num:
                    plays.extend(_collection_combination(hand.cards[start_ind:i], num))
                cur_rank = hand.cards[i].rank
                start_ind = i
                counter = 1

        if counter >= num:
            plays.extend(_collection_combination(hand.cards[start_ind:], num))

        return plays

    def _enumerate_straights(cards, c_count):
        if len(c_count) == 1:
            return [[card] for card in cards]

        straights = []
        for i in range(c_count[0]):
            sub_straights = _enumerate_straights(cards[c_count[0]:], c_count[1:])
            for s in sub_straights:
                new_s = [cards[i]]
                new_s.extend(s)
                straights.append(new_s)

        return straights

    hand = sort_cards(hand)
    if hand.num_cards() == 0:
        return []

    if type == "single":
        return [CardCollection([card]) for card in hand.cards]
    elif type == "double":
        return _enumerate_multiples(hand, 2)
    elif type == "triple":
        return _enumerate_multiples(hand, 3)
    elif type == "quad":
        return _enumerate_multiples(hand, 4)
    elif type == "bomb":
        possible_plays = []
        quads = _enumerate_multiples(hand, 4)
        for q in quads:
            for card in hand.cards:
                if q.cards[0].rank != card.rank:
                    possible_plays.append(CardCollection.merge_collections((q, CardCollection([card]))))
        return possible_plays
    elif type == "fullhouse":
        possible_plays = []
        doubles = _enumerate_multiples(hand, 2)
        triples = _enumerate_multiples(hand, 3)
        for d in doubles:
            for t in triples:
                if d.cards[0].rank != t.cards[0].rank:
                    possible_plays.append(CardCollection.merge_collections((d, t)))
        return possible_plays
    elif type == "straight":
        possible_plays = []
        c_count = [0] * 15
        end_cards = []
        for card in hand.cards:
            c_count[card.rank - 1] += 1
            if card.rank == 1 or card.rank == 2:
                c_count[card.rank + 12] += 1
                end_cards.append(card)
        end_cards.extend(hand.cards)

        last_zero = -1
        cumul_start = 0
        cumul_cur = 0
        for i in range(len(c_count)):
            if c_count[i] == 0:
                last_zero = i
                cumul_start = cumul_cur
            else:
                cumul_cur += c_count[i]
                if i - last_zero >= 5:
                    play_list = _enumerate_straights(end_cards[cumul_start:cumul_cur], c_count[i-4:i+1])
                    possible_plays.extend([CardCollection(c_list) for c_list in play_list])
                    cumul_start += c_count[i - 4]
        return possible_plays
    elif type == "flush":
        possible_plays = []
        card_suits = {'C': [], 'D': [], 'H': [], 'S': []}
        for card in hand.cards:
            card_suits[card.suit].append(card)
        for suit in card_suits:
            possible_plays.extend(_collection_combination(card_suits[suit], 5))
        return possible_plays
    elif type == "straightflush":
        possible_plays = []
        flushes = search_plays(hand, "flush")
        for f in flushes:
            play, _ = identify_play(f)
            if play == "straightflush":
                possible_plays.append(f)
        return possible_plays
    else:
        raise InvalidHandTypeException("That hand type is not recognized.")


class InvalidComparisonException(Exception):
    pass


class InvalidHandTypeException(Exception):
    pass


class BigTwoEnv:
    def __init__(self, num_players=4):
        self.num_players = num_players
        self.player_cards = None
        self.history = None
        self.last_play = None
        self.pass_only = None
        self.player_card_count = None
        self.turn = None
        self.mode = None
        self.start = False
        self.done = True

    def reset(self):
        deck = Deck()
        deck.shuffle()
        self.player_cards = [sort_cards(hand) for hand in deck.deal(self.num_players)]
        self.player_card_count = [pc.num_cards() for pc in self.player_cards]
        self.history = [CardCollection()]
        self.last_play = None
        self.pass_only = [False] * self.num_players
        self.mode = "any"
        self.start = True
        self.done = False

        for i in range(len(self.player_cards)):
            if self.player_cards[i].contains(Card(3, 'C')):
                self.turn = i

        return self.get_state()

    def get_state(self):
        return BigTwoState(self.turn, self.player_cards[self.turn], self.player_card_count, self.history,
                           self.last_play, self.pass_only, self.mode, self.start, self.done)

    def is_valid(self, action):
        play, play_rep = identify_play(action)
        if play == "unknown":
            return False

        for card in action.cards:
            if not self.player_cards[self.turn].contains(card):
                return False

        if self.mode == "any":
            if play == "pass":
                return False
            if self.start:
                return action.contains(Card(3, 'C'))
            else:
                return True

        if play == "pass":
            return True
        elif self.pass_only[self.turn]:
            return False

        if self.mode == play:
            return compare_plays(action, self.last_play) == 1

        if play == "straightflush" or play == "bomb":
            return compare_plays(action, self.last_play) == 1

        if play in hand_vals and self.mode == "fivecard":
            return compare_plays(action, self.last_play) == 1

        return False

    def step(self, action):
        valid = self.is_valid(action)
        if not valid:
            if self.start:
                action = CardCollection([Card(3, 'C')])
                print("Warning: invalid play was submitted, playing 3C single...")
            elif self.mode == "any":
                chosen_card = self.player_cards[self.turn].cards[0]
                action = CardCollection([chosen_card])
                print("Warning: invalid play was submitted, playing {} single...".format(chosen_card))
            else:
                action = CardCollection()
                print("Warning: invalid play was submitted, passing turn...")

        play, play_rep = identify_play(action)
        if self.mode == "any":
            if play == "single" or play == "double" or play == "triple" or play == "quad":
                self.mode = play
            else:
                self.mode = "fivecard"

        if play == "bomb" or play == "straightflush":
            self.mode = "fivecard"

        if play == "pass":
            self.pass_only[self.turn] = True
            if len(self.history) >= (self.num_players - 2):
                all_pass = True
                for past_play in self.history[-(self.num_players - 2):]:
                    if past_play.num_cards() != 0:
                        all_pass = False
                if all_pass:
                    self.pass_only = [False] * self.num_players
                    self.mode = "any"

        reward = action.num_cards() / 5.0

        self.player_cards[self.turn].subtract(action)
        self.player_card_count[self.turn] -= action.num_cards()
        self.history.append(action)
        if play != "pass":
            self.last_play = action
        self.start = False

        nonzero = 0
        for count in self.player_card_count:
            if count > 0:
                nonzero += 1
        if self.player_card_count[self.turn] == 0 and play != "pass":
            reward += 2.0 * nonzero
        if nonzero <= 1:
            self.done = True

        self.turn = (self.turn + 1) % self.num_players

        while self.mode == "any" and self.player_card_count[self.turn] == 0:
            self.turn = (self.turn - 1) % self.num_players

        return self.get_state(), reward


class BigTwoState:
    def __init__(self, turn, hand, player_card_count, history, last_play, pass_only, mode, start, done):
        self.turn = turn
        self.hand = hand
        self.player_card_count = player_card_count
        self.history = history
        self.last_play = last_play
        self.pass_only = pass_only
        self.mode = mode
        self.start = start
        self.done = done

    def get_valid_moves(self):
        if self.done:
            return []
        if self.pass_only[self.turn]:
            return [CardCollection()]

        possible_plays = []
        if self.mode == "any" or self.mode == "single":
            possible_plays.extend(search_plays(self.hand, "single"))
        if self.mode == "any" or self.mode == "double":
            possible_plays.extend(search_plays(self.hand, "double"))
        if self.mode == "any" or self.mode == "triple":
            possible_plays.extend(search_plays(self.hand, "triple"))
        if self.mode == "any" or self.mode == "quad":
            possible_plays.extend(search_plays(self.hand, "quad"))
        if self.mode == "any" or self.mode == "fivecard":
            possible_plays.extend(search_plays(self.hand, "straight"))
            flushes = search_plays(self.hand, "flush")
            pure_flushes = []
            for f in flushes:
                play, _ = identify_play(f)
                if play == "flush":
                    pure_flushes.append(f)
            possible_plays.extend(pure_flushes)
            possible_plays.extend(search_plays(self.hand, "fullhouse"))
        else:
            possible_plays.extend(search_plays(self.hand, "straightflush"))

        possible_plays.extend(search_plays(self.hand, "bomb"))

        valid_plays = []
        if self.start:
            for play in possible_plays:
                if play.contains(Card(3, 'C')):
                    valid_plays.append(play)
            return valid_plays
        else:
            if self.mode == "any":
                return possible_plays
            else:
                valid_plays.append(CardCollection())
                for play in possible_plays:
                    if compare_plays(play, self.last_play) == 1:
                        valid_plays.append(play)
                return valid_plays


if __name__ == "__main__":
    new_env = BigTwoEnv(num_players=4)
    state = new_env.reset()
    done = False
    while not done:
        print("\nPlayer {}'s turn to play {}.".format(state.turn, state.mode))
        if state.pass_only[state.turn]:
            print("Since this player passed last turn, they can only pass until a new round begins.")
        print("Current cards: {}".format(state.hand))
        poss_moves = state.get_valid_moves()
        action = random.choice(poss_moves)
        print("Trying to play action {}".format(action))
        state, reward = new_env.step(action)
        done = state.done
        print("Played action {} and obtained reward {}.".format(action, reward))
        input("Press enter to continue...")
