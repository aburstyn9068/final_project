import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances

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





