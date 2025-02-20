import streamlit as st
import pandas as pd
from skillcorner.client import SkillcornerClient

# get connection to api
@st.cache_resource
def get_skillcorner_connection():
    client = SkillcornerClient(username=st.secrets.sc_username, password=st.secrets.sc_password)
    return client

# dict name-id of available competition editions
@st.cache_data
def get_available_competition_editions():
    client = get_skillcorner_connection()
    response = client.get_competition_editions({'user': 'true'})

    return_dict = {}
    for item in response:
        return_dict[item['name']] = item['id']

    return return_dict

# given the competition id get a dict name-id with the team names
def get_teams_for_competition_editions(competition_editions_id_list):
    # get the data
    client = get_skillcorner_connection()
    response = client.get_teams(params={'competition_edition': ",".join(competition_editions_id_list)})

    return_dict = {}

    for item in response:
        return_dict[item['name']] = item['id']

    return return_dict

# query the off ball runs end point
@st.cache_data
def get_off_runs_data(params):
    client = get_skillcorner_connection()
    response = client.get_in_possession_off_ball_runs(params=params)

    return response

# query the physical end point
@st.cache_data
def get_physical_data(params):
    client = get_skillcorner_connection()
    response = client.get_physical(params=params)

    return response

# query the pressures end point
@st.cache_data
def get_pressure_data(params):
    client = get_skillcorner_connection()
    response = client.get_in_possession_on_ball_pressures(params=params)

    return response

# query the passes end point
@st.cache_data
def get_passes_data(params):
    client = get_skillcorner_connection()
    response = client.get_in_possession_passes(params=params)

    return response

@st.cache_data
def transform_data_scouting(df_left, df_right, metrics_list):
    complete_df = pd.concat([df_left, df_right], ignore_index=True)
    grouped_df = complete_df.groupby(['player_id', 'short_name'])[metrics_list].mean().reset_index()
    grouped_df[metrics_list] = grouped_df[metrics_list].round(2)

    return grouped_df