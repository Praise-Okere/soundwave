# pyrefly: ignore [missing-import]
from surprise import SVD, Dataset, Reader
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np

def generate_synthetic_interactions(df, num_users=500):
    """Generate synthetic interactions for training the CF model"""
    interactions = []
    track_ids = df['track_id'].tolist()
    genres = df['track_genre'].tolist()
    track_to_genre = dict(zip(track_ids, genres))
    
    unique_genres = df['track_genre'].unique()
    
    for user_id in range(1, num_users + 1):
        # User prefers 1-3 genres
        pref_genres = np.random.choice(unique_genres, size=np.random.randint(1, 4), replace=False)
        
        # User rates 5-20 tracks
        num_ratings = np.random.randint(5, 21)
        rated_tracks = np.random.choice(track_ids, size=num_ratings, replace=False)
        
        for track_id in rated_tracks:
            track_genre = track_to_genre[track_id]
            if track_genre in pref_genres:
                rating = np.random.choice([4, 5], p=[0.4, 0.6]) # High rating
            else:
                rating = np.random.choice([1, 2, 3], p=[0.2, 0.3, 0.5]) # Lower rating
            
            interactions.append({
                'user_id': user_id,
                'track_id': track_id,
                'rating': rating
            })
            
    return pd.DataFrame(interactions)

def train_svd(ratings_data):
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(
        ratings_data[['user_id', 'track_id', 'rating']], reader)
    trainset = data.build_full_trainset()
    model = SVD(n_factors=100, lr_all=0.005, n_epochs=20)
    model.fit(trainset)
    return model

def get_cf_score(model, user_id, track_id):
    try:
        prediction = model.predict(user_id, track_id)
        # normalise to [0, 1]
        return (prediction.est - 1) / 4
    except Exception:
        # Fallback to mean rating or 0.5 if prediction fails
        return 0.5
