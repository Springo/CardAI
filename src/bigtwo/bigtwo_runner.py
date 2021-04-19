from src.card_data_structures import CardCollection
from src.bigtwo.bigtwo_env import BigTwoEnv
from src.bigtwo.bigtwo_agents import RandomAgent, HumanAgent


def run(players, verbose=False):
    assert len(players) >= 2

    new_env = BigTwoEnv(num_players=len(players))
    state = new_env.reset()
    num_finished = 0
    done = False
    while not done:
        cur_turn = state.turn

        if state.pass_only[cur_turn] or state.player_card_count[cur_turn] == 0:
            if verbose:
                print("\nPlayer {} must pass.".format(cur_turn + 1))
            action = CardCollection()
        else:
            if verbose:
                print("\nPlayer {}'s turn to play {}.".format(cur_turn + 1, state.mode))
            action = players[cur_turn].get_action(state)

        state, reward = new_env.step(action)
        done = state.done
        if verbose:
            print("Played action {} and obtained reward {}.".format(action, reward))
        else:
            print("Player {} played {}.".format(cur_turn + 1, action))

        if state.player_card_count[cur_turn] == 0 and action.num_cards() > 0:
            if num_finished == 0:
                print("Player {} finished in 1st place!".format(cur_turn + 1))
            elif num_finished == 1:
                print("Player {} finished in 2nd place!".format(cur_turn + 1))
            elif num_finished == 2:
                print("Player {} finished in 3rd place!".format(cur_turn + 1))
                for i in range(len(players)):
                    if state.player_card_count[i] > 0:
                        print("Player {} lost!".format(i + 1))
            num_finished += 1


if __name__ == "__main__":
    players = [HumanAgent(), RandomAgent(), RandomAgent(), RandomAgent()]
    run(players, verbose=False)
