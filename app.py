import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# Create interactive dashboard
# Title
st.write("""
# NBA Player Replacement
This app can be used to determine who will be a suitable replacement for a player on your roster.
""")

# Upload the data only when first opening the app
flag = False
if flag == False:
    df = pd.read_csv("FINAL.csv")
    # Get a list of the teams and add "ALL" to select all teams
    team_list = np.append(["ALL"], df["Tm"].sort_values().unique())
    # Set flag to true to the csv file is not reloaded
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

    position = st.sidebar.selectbox("Position", position_list)

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

# Graph the player stats
player_stats = df.loc[df["Player"]==input_data.player[0]]
st.subheader("Player Stats:")
st.write(player_stats)
st.bar_chart(player_stats)

#####Matplot example
speed = [0.1, 17.5, 40, 48, 52, 69, 88]
lifespan = [2, 8, 70, 1.5, 25, 12, 28]
index = ['snail', 'pig', 'elephant',
         'rabbit', 'giraffe', 'coyote', 'horse']
df_test = pd.DataFrame({'speed': speed,
                   'lifespan': lifespan}, index=index)
fig, ax = plt.subplots()
#ax = df_test.plot.bar(rot=0)
x = np.arange(len(index))
width = 0.35
ax.bar(x - width/2, lifespan, width, label="Lifespan")
ax.bar(x + width/2, speed, width, label="Speed")
ax.set_xticks(x)
ax.set_xticklabels(index)
ax.legend()
st.pyplot(fig)
#ax.bar(rot=0)
#st.pyplot(fig)
#st.bar_chart(df_test)

#######Streamlit example
# arr = np.random.normal(1, 1, size=100)
# fig, ax = plt.subplots()
# ax.hist(arr, bins=20)
# st.pyplot(fig)

#################


