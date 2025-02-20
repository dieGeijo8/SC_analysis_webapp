from Modules.Endpoints import *
from Modules.SkillCornerVisualization import *

# Get off ball runs data - left and right
runs_params_left = {
    'competition_edition': '251,257',
    'group': 'WideAttacker',
    'age__lte': 27,
    'channel': 'wide_left',
    'third':  'attacking',
    'run_type': 'run_in_behind,pulling_wide_run,overlap_run',
    'group_by': 'player',
    'count_match__gte': 5
}
runs_left = pd.DataFrame(get_off_runs_data(runs_params_left))
runs_params_right = {
    'competition_edition': '251,257',
    'group': 'WideAttacker',
    'age__lte': 27,
    'channel': 'wide_right',
    'third':  'attacking',
    'run_type': 'run_in_behind',
    'group_by': 'player',
    'count_match__gte': 5
}
runs_right = pd.DataFrame(get_off_runs_data(runs_params_right))
# We keep average by player of dangerous run per match, dangerous run targeted, dangerous run received
runs_complete_df = transform_data_scouting(runs_left, runs_right, ['count_dangerous_runs_in_behind_per_match',
                                     'count_dangerous_runs_in_behind_targeted_per_match',
                                     'count_dangerous_runs_in_behind_received_per_match'])


pressures_params_left = {
    'competition_edition': '251,257',
    'group': 'WideAttacker',
    'age__lte': 27,
    'channel': 'wide_left',
    'third':  'attacking',
    'pressure_intensity': 'high',
    'group_by': 'player',
    'count_match__gte': 5
}
pressures_left = pd.DataFrame(get_pressure_data(pressures_params_left))
pressures_params_right = {
    'competition_edition': '251,257',
    'group': 'WideAttacker',
    'age__lte': 27,
    'channel': 'wide_right',
    'third':  'attacking',
    'pressure_intensity': 'high',
    'group_by': 'player',
    'count_match__gte': 5
}
pressures_right = pd.DataFrame(get_pressure_data(pressures_params_right))
# We keep average by player of ball retention under high pressure and completed dangerous passes
pressures_complete_df = transform_data_scouting(pressures_left, pressures_right, ['ball_retention_ratio_under_high_pressure',
                                     'count_completed_dangerous_passes_under_high_pressure_per_match'])


passes_params_left = {
    'competition_edition': '251,257',
    'group': 'WideAttacker',
    'age__lte': 27,
    'channel': 'wide_left',
    'third':  'attacking',
    'run_type': 'cross_receiver_run',
    'group_by': 'player',
    'count_match__gte': 5
}
passes_left = pd.DataFrame(get_passes_data(passes_params_left))
passes_params_right = {
    'competition_edition': '251,257',
    'group': 'WideAttacker',
    'age__lte': 27,
    'channel': 'wide_left',
    'third':  'attacking',
    'run_type': 'all',
    'group_by': 'player',
    'count_match__gte': 5
}
passes_right = pd.DataFrame(get_passes_data(passes_params_right))
# We keep average by player of dangerous run per match, dangerous run targeted, dangerous run received
passes_complete_df = transform_data_scouting(passes_left, passes_right, ['pass_completion_ratio_to_runs',
                                                                         'count_completed_pass_to_runs_leading_to_shot_per_match'])

# Merge three DataFrames on 'player_id'
merged_df = runs_complete_df.merge(pressures_complete_df, on="player_id", how="outer").merge(passes_complete_df, on="player_id", how="outer")
# Fill NaN values with 0
merged_df = merged_df.dropna()
merged_df = merged_df.drop(["short_name", "short_name_y"], axis=1)
merged_df = merged_df.rename(columns={"short_name_x": "short_name"})

columns_to_normalize = list(merged_df.columns)[2:]
norm_merged_df = merged_df.copy()
norm_merged_df[columns_to_normalize] = (round((norm_merged_df[columns_to_normalize] - norm_merged_df[columns_to_normalize].min())
                                   / (norm_merged_df[columns_to_normalize].max() - norm_merged_df[columns_to_normalize].min()), 2))

st.title('Scouting of winger for AC Milan')

st.subheader('Data used', divider='grey')

options = ["Hide", "Runs data", "Pressures data", "Passes data"]
pill_selection = st.pills("See data used", options, selection_mode="single", default='Hide')
if pill_selection == 'Runs data':
    st.dataframe(runs_complete_df)
if pill_selection == 'Pressures data':
    st.dataframe(pressures_complete_df)
if pill_selection == 'Passes data':
    st.dataframe(passes_complete_df)


st.subheader('Weighted formula', divider='grey')

col1, col2, col3 = st.columns(3)
with col1:
    runs_weight = st.number_input('Runs data', min_value=0.0, max_value=1.0, step=0.1, value=0.5)
with col2:
    pressures_weight = st.number_input('Pressures data', min_value=0.0, max_value=1.0, step=0.1, value=0.2)
with col3:
    passes_weight = st.number_input('Passes data', min_value=0.0, max_value=1.0, step=0.2, value=0.3)

weights = dict(zip(list(norm_merged_df.columns)[2:], 3*[runs_weight]+2*[pressures_weight]+2*[passes_weight]))
# Compute the weighted sum
# Compute weighted score dynamically
norm_merged_df["weighted_score"] = sum(
    norm_merged_df[col] * weight for col, weight in weights.items()
)
# Sort by 'weighted_score' in descending order
norm_merged_df = norm_merged_df.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
st.dataframe(norm_merged_df)

st.subheader('Charts', divider='grey')
col1, col2, _ = st.columns(3)
with col1:
    options = ["Hide", "Show graphs"]
    pill_viz_selection = st.pills("", options, selection_mode="single", default='Hide')
with col2:
    top_n = st.number_input('Show top n', min_value=0, max_value=10, step=1, value=5)

if pill_viz_selection != 'Hide':
    table_metrics = {'count_dangerous_runs_in_behind_per_match': 'Dang.Runs in behind per match',
                    'count_dangerous_runs_in_behind_targeted_per_match': 'Dang.Runs in b. targeted per match',
                    'count_dangerous_runs_in_behind_received_per_match': 'Dang.Runs in b. received per match',
                    'ball_retention_ratio_under_high_pressure': 'Ball ret. under high pressure',
                    'count_completed_dangerous_passes_under_high_pressure_per_match': 'Compl.dang. passes under h.p.',
                    'pass_completion_ratio_to_runs': 'Pass ratio to runs',
                    'count_completed_pass_to_runs_leading_to_shot_per_match': 'Passes to runs to shot per match'}
    top_n_names = list(norm_merged_df['short_name'])[:top_n]

    fig_1 = summary_table_scouting(table_metrics, merged_df, top_n_names)
    st.pyplot(fig_1)

    radar_player = st.selectbox('Pick a player', top_n_names, index=0)
    fig_2 = radar_plot_scouting(table_metrics, merged_df, radar_player)
    st.pyplot(fig_2)