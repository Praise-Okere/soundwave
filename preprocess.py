import pandas as pd
from sklearn.preprocessing import MinMaxScaler

NUMERIC_COLS = [
    'danceability', 'energy', 'valence', 'tempo',
    'loudness', 'speechiness', 'acousticness', 'instrumentalness'
]

def load_and_clean(filepath):
    df = pd.read_csv(filepath)
    df[NUMERIC_COLS] = df[NUMERIC_COLS].fillna(df[NUMERIC_COLS].mean())
    scaler = MinMaxScaler()
    df[NUMERIC_COLS] = scaler.fit_transform(df[NUMERIC_COLS])
    df = df.dropna(subset=['track_name', 'artists', 'track_genre'])
    return df, scaler
