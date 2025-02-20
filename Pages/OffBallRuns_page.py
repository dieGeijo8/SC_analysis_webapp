from Modules.SkillCornerVisualization import *
from Modules.Endpoints import *

## INTRO
st.title('Off ball runs')
intro_offballruns = '''
Set the input parameters and explore the **data** and **graphs** in the below section.  
'''
st.markdown(intro_offballruns)

st.header('Input parameters', divider='gray')
input_offballruns = '''
Set the input parameters.  
'''
st.markdown(input_offballruns)

## INPUT DATA SECTION
# Get the available competitions
competitions_dict = get_available_competition_editions()
# other parameters - static set of values
position_group = ["CentralDefender", "FullBack", "Midfield", "WideAttacker", "CenterForward"]
roles = [
    "GK", "LCB", "CB", "RCB", "LWB", "LB", "RB", "RWB",
    "LDM", "DM", "RDM", "LM", "CM", "RM", "AM",
    "LW", "RW", "LF", "RF", "CF", "SUB"
]
third = ["all", "defending", "middle", "attacking"]
group_by = ["none", "player", "team", "match", "competition"]

# Competitions multiselect
competition_names = list(competitions_dict.keys())
selected_competitions = st.multiselect(
    "Select among the available competitions",
    competition_names,
    key='offball_comp_widget'
)
# Get the selected competition IDs
selected_competitions_id = [str(competitions_dict[item]) for item in selected_competitions]

# Fetch available teams for selected competitions - only if at least one competition is selected
teams_dict = get_teams_for_competition_editions(selected_competitions_id) if selected_competitions else {}
teams_names = list(teams_dict.keys()) if selected_competitions else []
# Teams multiselect
selected_teams = st.multiselect(
    "Select among the available teams",
    teams_names,
    disabled=not selected_competitions,  # Disable if no competitions are selected
    key='offball_teams_widget'
)
# Get the selected team IDs
selected_teams_id = [str(teams_dict[item]) for item in selected_teams]

# Positions widget
position_multiselect = st.multiselect(
    "Select position group",
    position_group,
    key='offball_pos_widget'
)

# Roles widget
role_multiselect = st.multiselect(
    "Select a role group",
    roles,
    key='offball_roles_widget'
)

# Third widget
third_radio = st.radio(
    "Select a specific third of the peach",
    third,
    horizontal=True,
    key='offball_third_widget'
)

# Grouping widget
grouping_radio = st.radio(
    "Specify the aggregation level",
    group_by,
    horizontal=True,
    key='offball_grouping_widget'
)

if "api_params" not in st.session_state:
    st.session_state.query_params = None  # Stores the last query params
if "api_response" not in st.session_state:
    st.session_state.api_response = None  # Stores the last data retrieved

## SHOW DATA SECTION
st.divider()
set_params = {}
if st.button("Retrieve data"):
    try:
        # Collect the parameters set in the input widgets
        set_params = {
            key: value
            for key, value in {
                'competition_edition': ",".join(selected_competitions_id) if selected_competitions_id else None,
                'team': ",".join(selected_teams_id) if selected_teams_id else None,
                'group': ",".join(position_multiselect) if position_multiselect else None,
                'role': ",".join(role_multiselect) if role_multiselect else None,
                'third': third_radio if third_radio else None,
                'group_by': grouping_radio if (grouping_radio and grouping_radio != 'none') else None
            }.items()
            if value  # Only include keys where the value is not empty or None
        }
        # Assign to session state variable
        st.session_state.query_params = set_params
        # Get the data
        response = get_off_runs_data(set_params)
        # Assign to session state variable
        st.session_state.api_response = response
    except:
        st.error("Error retrieving data. Please try refining your selection or reload the page.")
        st.stop()

    # For the charts not to change until new data retrieved
    if 'group_by' in set_params:
        st.session_state.current_grouping = set_params['group_by']
    else:
        st.session_state.current_grouping = None

if st.session_state.api_response:
    # Display 'raw' data
    st.subheader('Data', divider='grey')
    display_options = ['Table', 'Json']
    display_selection = st.segmented_control("Choose how to see the data", display_options, selection_mode="single", default="Table")

    response_df = pd.DataFrame(st.session_state.api_response)
    if display_selection == 'Table':
        st.dataframe(response_df)
    else:
        st.write(st.session_state.api_response)


    # Display scatter plot
    st.subheader('Scatterplot', divider='grey')
    # Metric selection
    selectbox_options = list(response_df.columns)
    selectbox_options = selectbox_options[selectbox_options.index('count_runs_in_sample'):]
    index_default_x = selectbox_options.index('count_runs_targeted_per_match')
    index_default_y = selectbox_options.index('count_runs_received_per_match')
    x_metric = st.selectbox('Select the metric for x', options=selectbox_options, index=index_default_x)
    y_metric = st.selectbox('Select the metric for y', options=selectbox_options, index=index_default_y)
    # Chart based on selected grouping - player if none
    if st.session_state.current_grouping == 'player' or st.session_state.current_grouping is None:
        fig = scatter_chart_off_ball_runs(x_metric, y_metric, 'short_name', response_df, )
        st.pyplot(fig)
    elif st.session_state.current_grouping == 'team':
        fig = scatter_chart_off_ball_runs(x_metric, y_metric, 'team_name', response_df)
        st.pyplot(fig)
    else:
        st.write('Plot available only when grouping by player or team.')

    # Display bar plot
    st.subheader('Barplot', divider='grey')
    # Metric selection
    index_default = selectbox_options.index('count_runs_targeted_per_match')
    x_metric = st.selectbox('Select the metric', options=selectbox_options, index=index_default)
    # Chart based on selected grouping - player if none
    if st.session_state.current_grouping == 'player' or st.session_state.current_grouping is None:
        fig = barplot_chart_off_ball_runs(x_metric, 'short_name', response_df)
        st.pyplot(fig)
    elif st.session_state.current_grouping == 'team':
        fig = scatter_chart_off_ball_runs(x_metric, 'team_name', response_df)
        st.pyplot(fig)
    else:
        st.write('Plot available only when grouping by player or team.')



