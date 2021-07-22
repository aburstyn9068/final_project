import streamlit as st
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pyvis import network as net
from stvis import pv_static
import plotly.graph_objects as go
#import distance
from sklearn.metrics.pairwise import euclidean_distances
import networkx as nx

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
    #return df1[1:6]
    return df1.loc[df1["Player"]!=player].head()

# Network graph function (https://plotly.com/python/network-graphs/)
def network(input_data, clustered_df):

    # Create the edge list
    from_list = []
    to_list = []
    for index, row in clustered_df.iterrows():
        from_list.append(input_data.player[0])
        to_list.append(row["Player"])
    graph_df = pd.DataFrame({"from": from_list, "to": to_list})

    # Calculate coordinates for nodes based on distance from selected player
    position_list = [
        [0, ((clustered_df["Distance"][1]**2)-((.5-0)**2))**.5], 
        [.25, ((clustered_df["Distance"][2]**2)-((.5-.25)**2))**.5], 
        [.5, ((clustered_df["Distance"][3]**2)-((.5-.5)**2))**.5], 
        [.75, ((clustered_df["Distance"][4]**2)-((.5-.75)**2))**.5], 
        [1, ((clustered_df["Distance"][5]**2)-((.5-1)**2))**.5]
    ]

    G = nx.from_pandas_edgelist(graph_df, source="from", target="to")

    edge_x = []
    edge_y = []
    for position in position_list:
        x0, y0 = [.5,0]
        x1, y1 = position
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

    node_x = [.5]
    node_y = [0]
    for position in position_list:
        x, y = position
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[input_data.player[0], clustered_df.Player[1], clustered_df.Player[2], 
            clustered_df.Player[3], clustered_df.Player[4], clustered_df.Player[5]],
        textposition="bottom center",
        marker=dict(
            showscale=True,
            # colorscale options
            #'Greys' | 'YlGnBu' | 'Greens' | 'YlOrRd' | 'Bluered' | 'RdBu' |
            #'Reds' | 'Blues' | 'Picnic' | 'Rainbow' | 'Portland' | 'Jet' |
            #'Hot' | 'Blackbody' | 'Earth' | 'Electric' | 'Viridis' |
            colorscale='Greens',
            reversescale=False,
            color=[],
            size=50,
            colorbar=dict(
                thickness=15,
                title='Player Salary',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = [int(player_stats["Salary"].values[0])]
    node_text = [f"Salary: {int(player_stats.Salary.values[0])}"]

    for index, row in clustered_df.iterrows():
        node_adjacencies.append(row["Salary"])
        #node_text.append(f"Salary: {row.Salary}")


    node_trace.marker.color = node_adjacencies
    #node_trace.text = node_text

    fig2 = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='<br>Network Graph of Closest Players to Selected Player',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    st.plotly_chart(fig2)

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
    
    # Display the network graph
    network(input_data, clustered_df)

    st.write("""
    The distance of the line connecting the players represents how closely related the players are.
    The shorter the line, the more closely related they are.
    The color of the bubble representing the players is scaled according to the players salary.
    """)
    
    # Line break
    st.markdown("***")
    
    # Player comparison graph

    # Get list of stats to display
    player1 = player_stats.drop(columns=["Player", "Pos", "Tm", "MP"])
    index = player1.columns

    # Display stats checkbox
    st.subheader("Select stats to display:")
    graph_index_selection = {}
    for stat in index:
        graph_index_selection[stat] = True

    # Create checkboxes
    cols = st.beta_columns(7)
    default_stats = ["FG", "FGA", "2P", "2PA", "TRB"]
    col_index = 0
    counter = 0
    for stat in graph_index_selection:
        # Set default stats to display
        #if (stat == "FG") or (stat == "FGA") or (stat == "2P") or (stat == "2PA") or (stat == "TRB"):
        if stat in default_stats:
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
    st.subheader("No players within selected salary range. Please select a higher salary bound")