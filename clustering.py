import pandas as pd
from sklearn.cluster import AgglomerativeClustering

def cluster(df1, player):
    #df = dataframe

    #df1 = df.loc[df["Pos"]==position]

    # Create the input variables
    X = df1.drop(columns=["Player", "Tm", "Pos", "Salary"])

    clustering = AgglomerativeClustering(n_clusters=13).fit(X)
    
    df1["Label"] = clustering.labels_

    player_label = df1.loc[df1["Player"]==player]["Label"].values[0]
    # Return the dataframe of top 5 players similar to selected player
    return df1.loc[(df1["Label"]==player_label)&(df1["Player"]!=player)].reset_index().drop(columns=["index"]).head(5)





