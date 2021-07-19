import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pyvis import network as net
from stvis import pv_static
import clustering

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

# Find the closest players
pos = df["Pos"].loc[df["Player"]==input_data.player[0]].values[0]
clustered_df = clustering.cluster(df.loc[df["Pos"]==pos], input_data.player[0])
clustered_df = clustering.cluster(df.loc[(df["Pos"]==pos)&(df["Salary"]<=input_data.salary[0])], input_data.player[0])
st.write(clustered_df)

# Graph the player stats
player_stats = df.loc[df["Player"]==input_data.player[0]]
st.subheader("Player Stats:")
st.write(player_stats)

#########Get closest player stats #######Need to update
player2_stats = clustered_df.head(1)
st.subheader("Player2 Stats:")
st.write(player2_stats)

# Network graph example
g=net.Network(height='500px', width='500px',heading='')
g.add_node(1)
g.add_node(2)
g.add_node(3)
g.add_edge(1,2, value=0, weight=0, distance=500, springLength=200)
g.add_edge(2,3, value=1, weight=.5, distance=100, springLength=1000)
g.add_edge(1,3, value=.5, weight=1, distance=100, springLength=200)
pv_static(g)

# Network graph test
g=net.Network(height='500px', width='500px',heading='')
g.add_node(input_data.player[0])
for index, row in clustered_df.iterrows():
    g.add_node(row["Player"])
    g.add_edge(input_data.player[0],row["Player"], value=5, weight=5)
pv_static(g)

#####Matplot example
speed = [0.1, 17.5, 40, 48, 52, 69, 88]
lifespan = [2, 8, 70, 1.5, 25, 12, 28]
index = ['snail', 'pig', 'elephant',
         'rabbit', 'giraffe', 'coyote', 'horse']
#df_test = pd.DataFrame({'speed': speed, 'lifespan': lifespan}, index=index)
fig, ax = plt.subplots()
x = np.arange(len(index))
width = 0.35
ax.bar(x - width/2, lifespan, width, label="Lifespan")
ax.bar(x + width/2, speed, width, label="Speed")
ax.set_xticks(x)
ax.set_xticklabels(index)
ax.legend()
st.pyplot(fig)

#####Player graph test
###########Scaling to keep certain columns
player1 = player_stats.drop(columns=["Player", "Pos", "Tm", "MP", "Salary"])
index = player1.columns
player1 = player1.to_numpy()

player2 = player2_stats.drop(columns=["Player", "Pos", "Tm", "MP", "Salary", "Label"])
player2 = player2.to_numpy()

fig, ax = plt.subplots()
x = np.arange(len(index))
width = 0.35
ax.bar(x - width/2, player1[0].reshape(-1), width, label=input_data.player[0])
ax.bar(x + width/2, player2[0].reshape(-1), width, label=player2_stats["Player"][0])
ax.set_xticks(x)
ax.set_xticklabels(index)
plt.xticks(rotation = 60)
ax.legend()
st.pyplot(fig)