from src.card_data_structures import CardCollection
from src.bigtwo.bigtwo_env import BigTwoEnv
from src.bigtwo.bigtwo_agents import RandomAgent, HumanAgent, GreedyAgent


def run(players, verbose=False):
    assert len(players) >= 2

    names = []
    for i in range(len(players)):
        if players[i].name is None:
            names.append("Player {}".format(i + 1))
        else:
            names.append("{} (Player {})".format(players[i].name, i + 1))

    new_env = BigTwoEnv(num_players=len(players))
    state = new_env.reset()
    num_finished = 0
    done = False
    while not done:
        cur_turn = state.turn
        must_pass = False

        if state.pass_only[cur_turn] or state.player_card_count[cur_turn] == 0:
            must_pass = True
            if verbose:
                print("\n{} must pass.".format(names[cur_turn]))
            action = CardCollection()
        else:
            if verbose:
                print("\n{}'s turn to play {}.".format(names[cur_turn], state.mode))
            action = players[cur_turn].get_action(state)

        state, reward = new_env.step(action)
        done = state.done
        if not must_pass:
            if verbose:
                print("Played action {} and obtained reward {}.".format(action, reward))
            else:
                if action.num_cards() > 0:
                    print("{} played {}.".format(names[cur_turn], action))
                else:
                    print("{} passed.".format(names[cur_turn]))

        if state.player_card_count[cur_turn] == 0 and action.num_cards() > 0:
            if num_finished == 0:
                print("{} finished in 1st place!".format(names[cur_turn]))
            elif num_finished == 1:
                print("{} finished in 2nd place!".format(names[cur_turn]))
            elif num_finished == 2:
                print("{} finished in 3rd place!".format(names[cur_turn]))
                for i in range(len(players)):
                    if state.player_card_count[i] > 0:
                        print("{} lost and had the remaining cards: {}".format(
                            names[i], new_env.player_cards[i]))
            num_finished += 1


if __name__ == "__main__":
    players = [HumanAgent("Kevin"), GreedyAgent("Bob"), GreedyAgent(), GreedyAgent()]
    run(players, verbose=False)
