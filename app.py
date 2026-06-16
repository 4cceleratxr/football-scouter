import streamlit as st
import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

import plotly.graph_objects as go

@st.cache_data
def load_data():
    df = pd.read_csv(
        r"C:\\Users\\KIIT0001\\Desktop\\Scouting_System Project\\data\\processed\\scouting_dashboard_data.csv"
    )

    df = df.drop_duplicates(
        subset=["Player"]
    )

    return df

df = load_data()

FEATURES = [

    "Gls",
    "Ast",

    "Sh",
    "SoT",

    "TklW",
    "Int",

    "Crs",

    "PPM"
]

CLUSTER_NAMES = {

    0: "Average Professionals",

    1: "Defense Specialists",

    2: "Fringe Players",

    3: "Great Attackers",

    7: "Elite Outliers"
}

scaler = MinMaxScaler()

scaled_features = scaler.fit_transform(
    df[FEATURES].fillna(0)
)

scaled_df = pd.DataFrame(
    scaled_features,
    columns=FEATURES
)

scaled_df["Player"] = df["Player"]

similarity_matrix = cosine_similarity(
    scaled_features
)

def get_similar_players(
    player_name,
    top_n=10
):

    player_index = df[
        df["Player"] == player_name
    ].index[0]

    scores = list(
        enumerate(
            similarity_matrix[player_index]
        )
    )

    scores = sorted(
        scores,
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for idx, score in scores[1:top_n+1]:

        results.append({

            "Player":
            df.iloc[idx]["Player"],

            "Position":
            df.iloc[idx]["Pos"],

            "Similarity":
            round(score*100,2)

        })

    return pd.DataFrame(results)

def find_young_alternatives(
    player_name,
    max_age=24,
    top_n=10
):

    player_index = df[
        df["Player"] == player_name
    ].index[0]

    scores = list(
        enumerate(
            similarity_matrix[player_index]
        )
    )

    scores = sorted(
        scores,
        key=lambda x: x[1],
        reverse=True
    )

    results = []

    for idx, score in scores:

        if idx == player_index:
            continue

        if df.iloc[idx]["Age"] > max_age:
            continue

        results.append({

            "Player":
            df.iloc[idx]["Player"],

            "Age":
            df.iloc[idx]["Age"],

            "Similarity":
            round(score*100,2)

        })

        if len(results) >= top_n:
            break

    return pd.DataFrame(results)

def create_radar(player_name):

    player = scaled_df[
        scaled_df["Player"] == player_name
    ].iloc[0]

    categories = FEATURES + [FEATURES[0]]

    values = [
        player[f]
        for f in FEATURES
    ]

    values += [values[0]]

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            name=player_name
        )
    )

    fig.update_layout(

        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0,1]
            )
        ),

        showlegend=False
    )

    return fig

def scouting_report(player_name):

    player = df[
        df["Player"] == player_name
    ].iloc[0]

    report = {

        "Goals": int(player["Gls"]),
        "Assists": int(player["Ast"]),
        "Shots": int(player["Sh"]),
        "Tackles Won": int(player["TklW"]),
        "Interceptions": int(player["Int"]),
        "Crosses": int(player["Crs"]),
        "PPM": round(float(player["PPM"]), 2)
    }

    print(report)

    return report

st.title(
    "Football Scouting Dashboard"
)

selected_player = st.selectbox(

    "Choose a Player",

    sorted(
        df["Player"].unique()
    )
)

player = df[
    df["Player"] == selected_player
].iloc[0]

st.subheader("Player Information")

st.write(
    f"Club: {player['Squad']}"
)

st.write(
    f"Position: {player['Pos']}"
)

cluster_name = CLUSTER_NAMES.get(
    player["Cluster"],
    "Unknown"
)

st.write(
    f"Archetype: {cluster_name}"
)

st.write(
    f"Age: {player['Age']}"
)

st.subheader(
    "Player Radar"
)

if player["Cluster"] == 7:

    st.warning(
        "Elite Statistical Outlier"
    )

st.plotly_chart(
    create_radar(
        selected_player
    ),
    use_container_width=True
)

st.subheader(
    "Most Similar Players"
)

st.dataframe(

    get_similar_players(
        selected_player
    )

)

st.subheader(
    "Young Alternatives"
)

st.dataframe(

    find_young_alternatives(
        selected_player
    )

)

st.subheader(
    "Scouting Report"
)

report = scouting_report(
    selected_player
)

st.json(report)