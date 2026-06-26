import os
import requests
import pandas as pd
import time
import random

GENRES = ['afrobeats', 'highlife', 'amapiano', 'hip-hop', 'r&b', 'gospel']
TRACKS_PER_GENRE = 100

def fetch_tracks():
    print("Connecting to iTunes API (No API keys needed!)...")
    data = []
    
    for genre in GENRES:
        print(f"Fetching tracks for genre: {genre}...")
        url = f"https://itunes.apple.com/search?term={genre}&entity=song&limit={TRACKS_PER_GENRE}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            results = response.json().get('results', [])
            
            for track in results:
                # iTunes doesn't give audio features like danceability, 
                # so we will simulate those features for our ML model 
                # just like we did with the sample data, but keep the REAL audio and metadata!
                
                preview_url = track.get('previewUrl')
                if not preview_url:
                    continue # Skip if no audio preview
                    
                data.append({
                    'track_id': str(track.get('trackId')),
                    'track_name': track.get('trackName', 'Unknown Title'),
                    'artists': track.get('artistName', 'Unknown Artist'),
                    'album_name': track.get('collectionName', 'Unknown Album'),
                    'track_genre': genre,
                    'popularity': random.randint(30, 100), # Simulate popularity
                    'duration_ms': track.get('trackTimeMillis', 200000),
                    # Simulated audio features for the ML model
                    'danceability': round(random.uniform(0.4, 0.9), 3),
                    'energy': round(random.uniform(0.4, 0.9), 3),
                    'key': random.randint(0, 11),
                    'loudness': round(random.uniform(-10.0, -3.0), 3),
                    'mode': random.choice([0, 1]),
                    'speechiness': round(random.uniform(0.05, 0.3), 3),
                    'acousticness': round(random.uniform(0.01, 0.4), 3),
                    'instrumentalness': round(random.uniform(0.0, 0.1), 3),
                    'liveness': round(random.uniform(0.05, 0.3), 3),
                    'valence': round(random.uniform(0.3, 0.9), 3),
                    'tempo': round(random.uniform(90.0, 140.0), 3),
                    'time_signature': 4,
                    'preview_url': preview_url
                })
                
        except Exception as e:
            print(f"Error fetching {genre}: {e}")
            
        # Be nice to the API
        time.sleep(1)
        
    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset=['track_id'])
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/spotify_tracks_clean.csv', index=False)
    print(f"\nSuccess! Saved {len(df)} REAL playable tracks to data/spotify_tracks_clean.csv")
    print(f"All of these tracks have 30-second audio previews available.")

if __name__ == "__main__":
    fetch_tracks()
