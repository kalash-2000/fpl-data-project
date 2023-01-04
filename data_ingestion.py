"""
Module to procure data of players playing in the English Premier League
We will be using this data to create visualizations

Created by 
Author 1: Kalash Gandhi <kalashgandhi.kg10@gmail.com>
Author 2: Anoushka Rao <anoushka410@gmail.com>
"""

##### Imports
import requests
import pandas as pd 

##### Constants
BASE_URL = 'https://fantasy.premierleague.com/api/' # base url for all FPL API endpoints
R = requests.get(BASE_URL+'bootstrap-static/').json() # get data from bootstrap-static endpoint


def create_players_df(response):
    """_summary_

    Args:
        response (_type_): _description_

    Returns:
        _type_: _description_
    """
    # create players dataframe
    players = pd.json_normalize(response['elements'])

    # create teams dataframe
    teams = pd.json_normalize(response['teams'])

    # get position information from 'element_types' field
    positions = pd.json_normalize(response['element_types'])

    # dictionary which maps team id to team name
    team_id_to_name = teams.set_index('id')['name'].to_dict() 

    # join team name
    players = players.merge(
        teams[['id', 'name']],
        left_on='team',
        right_on='id',
        suffixes=['_player', None]
    ).drop(['team', 'id'], axis=1)

    # join player positions
    players = players.merge(
        positions[['id', 'singular_name_short']],
        left_on='element_type',
        right_on='id'
    ).drop(['element_type', 'id'], axis=1)

    # rename columns
    players = players.rename(
        columns={'name':'team_name', 'singular_name_short':'position_name'}
    )

    # final dataframe with the following parameters
    players = players[
        ['id_player', 'first_name', 'second_name', 'web_name', 'team_name',
        'position_name']
    ]

    return team_id_to_name, players

def get_gameweek_history(player_id):
    """get all gameweek info for a given player_id

    Args:
        player_id (int): id of the player

    Returns:
        dataframe: dataframe of the player with information for all
                   the previous matches of the ongoing season.
    """
    
    # send GET request to
    # https://fantasy.premierleague.com/api/element-summary/{PID}/
    r = requests.get(
            BASE_URL + 'element-summary/' + str(player_id) + '/'
    ).json()
    
    # extract 'history' data from response into dataframe
    df = pd.json_normalize(r['history'])
    
    return df


def create_master_data():
    """_summary_

    Args:
        df_player_id (_type_): _description_

    Returns:
        _type_: _description_
    """
    players = create_players_df(R)[1]
    # create a dataframe with gameweek info of all the players
    players_history = players['id_player'].progress_apply(get_gameweek_history)

    # combine results into single dataframe
    players_history_full = pd.concat(df for df in players_history)

    # join web_name and position
    final_players_history = players.merge(
        players_history_full,
        left_on='id_player',
        right_on='element'
    )

    # rename the round column
    final_players_history.rename(columns={'round':'matchday'},inplace=True)

    # replace opponent team id with the name of team
    team_id_to_name = create_players_df(R)[0]
    final_players_history['opponent_team'] = final_players_history['opponent_team'].apply(lambda x: team_id_to_name[x])

    master_player_data = final_players_history[['id_player', 'first_name', 
                                            'second_name', 'web_name', 'team_name',
                                            'position_name','fixture', 'opponent_team',
                                            'total_points','was_home','team_h_score',
                                            'team_a_score', 'matchday','minutes',
                                            'goals_scored', 'assists', 'clean_sheets',
                                            'goals_conceded','penalties_saved',
                                            'yellow_cards','red_cards', 'saves',
                                            'bonus','bps', 'influence',
                                            'creativity','threat', 'ict_index',
                                            'starts', 'expected_goals', 'expected_assists',
                                            'expected_goal_involvements','expected_goals_conceded',
                                            'selected', 'transfers_in', 'transfers_out']]
    print(master_player_data.head())
    return master_player_data

