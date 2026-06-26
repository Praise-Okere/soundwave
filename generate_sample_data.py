import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
import random
import os

GENRES = ['afrobeats', 'highlife', 'fuji', 'amapiano', 'afropop', 'hip-hop', 'r&b', 'gospel', 'alte', 'pop', 'rock']
NUM_TRACKS = 800

def generate_data():
    data = []
    for i in range(NUM_TRACKS):
        genre = random.choice(GENRES)
        
        # Base features
        danceability = random.uniform(0.3, 0.9)
        energy = random.uniform(0.3, 0.9)
        valence = random.uniform(0.2, 0.9)
        tempo = random.uniform(60, 200)
        loudness = random.uniform(-60, 0)
        speechiness = random.uniform(0.0, 0.3)
        acousticness = random.uniform(0.0, 0.8)
        instrumentalness = random.uniform(0.0, 0.8)
        liveness = random.uniform(0.05, 0.6)
        
        # Bias features per genre
        if genre in ['afrobeats', 'amapiano']:
            danceability = random.uniform(0.7, 1.0)
            energy = random.uniform(0.6, 1.0)
        elif genre == 'gospel':
            acousticness = random.uniform(0.4, 1.0)
            valence = random.uniform(0.1, 1.0) # High variance
        elif genre in ['fuji', 'highlife']:
            tempo = random.uniform(90, 130)
            liveness = random.uniform(0.4, 0.9)
            instrumentalness = random.uniform(0.3, 0.8)
            
        # Introduce messiness (missing values)
        if random.random() < 0.05: danceability = np.nan
        if random.random() < 0.05: energy = np.nan
        if random.random() < 0.05: valence = np.nan
        
        data.append({
            'track_id': f'tr_{i:04d}',
            'track_name': f'{genre.capitalize()} Track {i}',
            'artists': f'Artist {random.randint(1, 100)}',
            'album_name': f'Album {random.randint(1, 50)}',
            'track_genre': genre,
            'popularity': random.randint(0, 100),
            'duration_ms': random.randint(120000, 300000), # 2 to 5 mins
            'danceability': danceability,
            'energy': energy,
            'key': random.randint(0, 11),
            'loudness': loudness,
            'mode': random.choice([0, 1]),
            'speechiness': speechiness,
            'acousticness': acousticness,
            'instrumentalness': instrumentalness,
            'liveness': liveness,
            'valence': valence,
            'tempo': tempo,
            'time_signature': random.choice([3, 4, 5])
        })
    
    df = pd.DataFrame(data)
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/spotify_tracks_clean.csv', index=False)
    print(f"Generated {NUM_TRACKS} tracks in data/spotify_tracks_clean.csv")

if __name__ == "__main__":
    generate_data()
