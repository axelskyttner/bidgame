import numpy as np
from collections import Counter


def keywithmaxval(d):
    """ a) create a list of the dict's keys and values;
        b) return the key with the max value"""
    v = list(d.values())
    k = list(d.keys())
    return k[v.index(max(v))]


def get_color():
    colorList = ["RED", "BLUE", "GREEN"]
    return np.random.choice(colorList)


def player_can_afford_it(transaction_list, player_name, bid):
    player_transactions = get_player_transactions(transaction_list,
                                                  player_name)
    money_left = get_total_money_left(player_transactions)
    if money_left >= bid:
        return True
    else:
        return False


def initialize_player_bids(players):
    player_bids = {}
    for player in players:
        player_bids[player.name] = None

    return player_bids


def get_player_score(transaction_list, player_name):
    most_common_color = get_nth_common_color(transaction_list, 1)
    snd_most_common_color = get_nth_common_color(transaction_list, 2)
    player_transactions = get_player_transactions(transaction_list,
                                                  player_name)
    player_colors = [trans['color'] for trans in player_transactions]

    highest_score = 3
    snd_highest_score = 1
    top_scores = [highest_score for color in player_colors if
                  color == most_common_color]

    snd_top_scores = [snd_highest_score for color in player_colors if
                      color == snd_most_common_color]

    return sum(top_scores) + sum(snd_top_scores)


def get_winner(transaction_list):
    players = get_players(transaction_list)
    player_scores = {}
    for player in players:
        player_score = get_player_score(transaction_list, player)
        player_scores[player] = player_score

    return keywithmaxval(player_scores)


def get_nth_common_color(transaction_list, n=1):
    color_list = [trans['color'] for trans in transaction_list]
    counted_list = Counter(color_list).most_common(n)

    # we do not want to ask for snd most common if only one color exists
    if len(counted_list) < n:
        return ""

    nth_most_common_color, nr_of_nth_color = counted_list[n-1]
    return nth_most_common_color


def is_game_finished(transaction_list):
    color_list = [trans['color'] for trans in transaction_list]
    most_common_color, nr_of_one_color = Counter(color_list).most_common(1)[0]
    return nr_of_one_color > 2


def get_players(transaction_list):
    return list(set(map(lambda x: x['name'], transaction_list)))


def get_player_transactions(trans_list, player_name):
    return [trans for trans in trans_list if trans['name'] == player_name]


def convert_state_dict_to_arr(state_dict):
    # following rgb convention
    current_color_index_dictionary = {
        'RED': 0,
        'GREEN': 1,
        'BLUE': 2
    }

    current_color = state_dict['color'].upper()
    current_color_index = current_color_index_dictionary[current_color]

    transaction_list = state_dict['transaction_list']
    bid_list = state_dict['player_bids']

    player_names = list(set(map(get_name, transaction_list)))

    players_information = {}
    for player_name in player_names:
        player_information = {}
        player_transactions = get_player_transactions(transaction_list,
                                                      player_name)
        nr_colors = count_number_of_colors(player_transactions)
        money_left = get_total_money_left(player_transactions)
        player_information['colors'] = nr_colors
        player_information['money_left'] = money_left
        player_information['current_bid'] = bid_list[player_name]
        players_information[player_name] = player_information

    nr_players = 2
    nr_colors = 3
    state_arr = np.zeros((nr_players+1, nr_colors+2))

    # add all the player specific information to array
    for player_index, player_name in enumerate(player_names):
        color_info = players_information[player_name]['colors']

        for color_index, color_value in enumerate(color_info.values()):
            state_arr[player_index][color_index] = color_value

        current_bid_index = -2
        player_bid = players_information[player_name]['current_bid']
        money_left_index = -1
        money_left = players_information[player_name]['money_left']
        state_arr[player_index][money_left_index] = money_left
        state_arr[player_index][current_bid_index] = player_bid

    # add the misc layer
    state_arr[-1, current_color_index] = 1

    return state_arr.flatten()


def count_number_of_colors(player_transactions):
    nr_colors = {
        'RED': 0,
        'BLUE': 0,
        'GREEN': 0
    }
    for player_transaction in player_transactions:

        nr_colors[player_transaction["color"].upper()] += 1

    return nr_colors


def get_total_money_left(player_transactions):
    total_amount = 100
    cost_list = [transaction['cost'] for transaction in player_transactions]
    money_spent = sum(cost_list)
    return total_amount - money_spent


def get_name(transaction):
    return transaction['name']
