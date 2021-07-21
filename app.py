import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pyvis import network as net
from stvis import pv_static
import plotly.graph_objects as go
#import distance
from sklearn.metrics.pairwise import euclidean_distances

# Player Distance function
def cluster(df1, player):
    # Create the input variables
    x = df1.loc[df1["Player"]==player]
    x = x.drop(columns=["Player", "Tm", "Pos", "Salary"])

    y = df1.drop(columns=["Player", "Tm", "Pos", "Salary"])

    # Calculate the distance between players
    df1["Distance"] = euclidean_distances(x, y)[0]

    # Sort the players by distance to the target
    df1 = df1.sort_values(by="Distance", ascending=True).reset_index(drop=True)
    
    # Return the top 5 closest players
    return df1[1:6]

# Create interactive dashboard
# Title
st.write("""
# NBA Player Replacement
This app can be used to determine who will be a suitable replacement for a player on your roster.
Using the input variables on the sidebar to the left, you can select the player you want to replace.
The players can be filtered by team and position. Additionally, you can select a maximum salary for 
replacement player options.

After a player is selected, the top 5 closest players to them will be displayed. The network graph 
seen below shows the relationship between the players.

The players stats can be compared using the interactive bar graph below. Stats and players can be 
added or removed from the graph by clicking on them.
""")

# Upload the data only when first opening the app
flag = False
if flag == False:
    df = pd.read_csv("FINAL.csv")
    # Get a list of the teams and add "ALL" to select all teams
    team_list = np.append(["ALL"], df["Tm"].sort_values().unique())
    # Set flag to true to the csv file is not reloaded
    flag = True

# Get user input values
def user_input():
    team = st.sidebar.selectbox("Team", team_list)

    if team == "ALL":
        position_list = np.append(["ALL"], df["Pos"].sort_values().unique())
        player_list = df["Player"].sort_values().unique()
        salary_min = int(df["Salary"].min())
        salary_max = int(df["Salary"].max())
    else:
        position_list = np.append(["ALL"], df["Pos"].loc[df["Tm"]==team].sort_values().unique())
        player_list = df["Player"].loc[df["Tm"]==team].sort_values().unique()
        salary_min = int(df["Salary"].min())
        salary_max = int(df["Salary"].max())

    position = st.sidebar.selectbox("Position", position_list)

    if (position != "ALL") & (team != "ALL"):
        player_list = df["Player"].loc[(df["Tm"]==team)&(df["Pos"]==position)].sort_values().unique()
    elif (position != "ALL") & (team == "ALL"):
        player_list = df["Player"].loc[df["Pos"]==position].sort_values().unique()

    player = st.sidebar.selectbox("Player", player_list)


    salary = st.sidebar.slider("Salary Requirement", salary_min, salary_max, salary_max)

    # Store and return input
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

# Display the selected player
player_stats = df.loc[df["Player"]==input_data.player[0]]

st.subheader("Selected Player:")
st.write(player_stats.reset_index(drop=True))

# Find the closest players with the same position to the selected player
pos = df["Pos"].loc[df["Player"]==input_data.player[0]].values[0]

input_df = df.loc[(df["Pos"]==pos)&(df["Salary"]<=input_data.salary[0])]

# Make sure there are players within the selected salary range
try:
    clustered_df = cluster(input_df, input_data.player[0])

    # Display top 5 closest players to selected player
    st.subheader("Ranked 5 Closest Players:")
    st.write(clustered_df)

    # Graph the player stats
    player_stats = df.loc[df["Player"]==input_data.player[0]]

    # # Network graph
    # st.subheader("Network Graph of Closest Players to Target Player")
    # g=net.Network(height='500px', width='700px', heading='')
    # g.add_node(input_data.player[0], value=int(player_stats["Salary"].values[0]), color="red")
    # for index, row in clustered_df.iterrows():
    #     g.add_node(row["Player"], value=row["Salary"])
    #     g.add_edge(input_data.player[0],row["Player"], value=row["Distance"], weight=5, distance=row["Distance"])
    # # Display network graph
    # pv_static(g)

    # st.write("""The width of the line connecting the players represents how closely related the players are.
    # The thicker the line, the more closely related they are.
    # The size of the bubble representing the players is sized according to the players salary.""")
    
    # Line break
    st.markdown("***")
    
    # Player comparison graph

    # Get list of stats to display
    player1 = player_stats.drop(columns=["Player", "Pos", "Tm", "MP"])
    index = player1.columns

    # Display stats checkbox
    st.write("Select stats to display:")
    graph_index_selection = {}
    for stat in index:
        graph_index_selection[stat] = True

    # Create checkboxes
    cols = st.beta_columns(7)
    col_index = 0
    counter = 0
    for stat in graph_index_selection:
        # Set default stats to display
        if (stat == "FG") or (stat == "FGA") or (stat == "2P") or (stat == "2PA") or (stat == "TRB"):
            graph_index_selection[stat] = cols[col_index].checkbox(stat, value=True)
        else:
            graph_index_selection[stat] = cols[col_index].checkbox(stat, value=False)
        counter+=1
        if (counter%4)==0:
            col_index+=1

    # Get a list of the selected stats to display
    x_labels = []
    for stat in graph_index_selection:
        if graph_index_selection[stat]:
            x_labels.append(stat)

    player1a = player_stats[x_labels]
    player1a = player1a.to_numpy()

    # Plotly bar graph
    fig = go.Figure(data=[
        go.Bar(name=input_data.player[0], x=x_labels, y=player1a[0].reshape(-1))
    ])
    for index, row in clustered_df.iterrows():
        player2b = row[x_labels]
        player2b = player2b.to_numpy()
        fig.add_trace(go.Bar(name=row["Player"], x=x_labels, y=player2b))
    # Change the bar mode
    fig.update_layout(title="Player Comparison", barmode='group')
    st.plotly_chart(fig)

except ValueError:
    st.write("No Players within selected salary range. Please select a higher salary bound")



######################################
import plotly.graph_objects as go

import networkx as nx

G = nx.random_geometric_graph(200, 0.125)

edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

node_x = []
node_y = []
for node in G.nodes():
    x, y = G.nodes[node]['pos']
    node_x.append(x)
    node_y.append(y)

node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers',
    hoverinfo='text',
    marker=dict(
        showscale=True,
        # colorscale options
        #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
        #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
        #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
        colorscale='YlGnBu',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

node_adjacencies = []
node_text = []
for node, adjacencies in enumerate(G.adjacency()):
    node_adjacencies.append(len(adjacencies[1]))
    node_text.append('# of connections: '+str(len(adjacencies[1])))

node_trace.marker.color = node_adjacencies
node_trace.text = node_text

fig2 = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                title='<br>Network graph made with Python',
                titlefont_size=16,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                annotations=[ dict(
                    text="Python code: <a href='https://plotly.com/ipython-notebooks/network-graphs/'> https://plotly.com/ipython-notebooks/network-graphs/</a>",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002 ) ],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
st.plotly_chart(fig2)