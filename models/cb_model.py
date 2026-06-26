import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

FEATURE_COLS = [
    'danceability', 'energy', 'valence', 'tempo',
    'loudness', 'speechiness', 'acousticness', 'instrumentalness'
]

def build_user_profile(df, liked_genres):
    mask = df['track_genre'].isin(liked_genres)
    genre_tracks = df[mask]
    if genre_tracks.empty:
        return df[FEATURE_COLS].mean().values
    return genre_tracks[FEATURE_COLS].mean().values

def get_cb_recommendations(df, user_profile, top_n=50):
    track_matrix = df[FEATURE_COLS].values
    profile_vec = user_profile.reshape(1, -1)
    scores = cosine_similarity(profile_vec, track_matrix)[0]
    top_indices = np.argsort(scores)[::-1][:top_n]
    recs = df.iloc[top_indices].copy()
    recs['cb_score'] = scores[top_indices]
    return recs
