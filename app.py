import streamlit as st
import pandas as pd
import numpy as np

# Create interactive dashboard
# Title
st.write("""
# NBA Player Replacement
This app can be used to determine who will be a suitable replacement for a player on your roster.
""")

# Upload the data only when first opening the app
flag = False
if flag == False:
    df = pd.read_csv("Payers_Stats(Bad_Info).csv")
    # Get a list of the teams and add "ALL" to select all teams
    team_list = np.append(["ALL"], df["Tm"].sort_values().unique())
    
    flag = True

# position_list = np.append(["ALL"], df["Pos"].sort_values().unique())
# player_list = df["Player"].sort_values().unique()
# salary_min = df["Salary"].min()
# salary_max = df["Salary"].max()

# Get user input values
def user_input():
    team = st.sidebar.selectbox("Team", team_list)

    if team == "ALL":
        position_list = np.append(["ALL"], df["Pos"].sort_values().unique())
        player_list = df["Player"].sort_values().unique()
        salary_min = df["Salary"].min()
        salary_max = df["Salary"].max()
    else:
        position_list = np.append(["ALL"], df["Pos"].loc[df["Tm"]==team].sort_values().unique())
        player_list = df["Player"].loc[df["Tm"]==team].sort_values().unique()
        salary_min = df["Salary"].min()
        salary_max = df["Salary"].max()

    position = st.sidebar.selectbox("Positon", position_list)

    if (position != "ALL") & (team != "ALL"):
        player_list = df["Player"].loc[(df["Tm"]==team)&(df["Pos"]==position)].sort_values().unique()
    elif (position != "ALL") & (team == "ALL"):
        player_list = df["Player"].loc[df["Pos"]==position].sort_values().unique()

    player = st.sidebar.selectbox("Player", player_list)


    salary = st.sidebar.slider("Salary Requirement", salary_min, salary_max, salary_max)

    # Store and reutrn input
    input_data = {
        "team": team,
        "position": position,
        "player": player,
        "salary": salary
    }
    features = pd.DataFrame(input_data, index=[0])
    return features

input_data = user_input()

player_list = df["Player"].loc[df["Tm"]==input_data["team"][0]].sort_values().unique()

# Display the input
st.subheader("User Inputs:")
st.write(input_data)

