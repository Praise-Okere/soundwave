import os
import pandas as pd
# pyrefly: ignore [missing-import]
import spotipy
# pyrefly: ignore [missing-import]
from spotipy.oauth2 import SpotifyClientCredentials
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET or "your_spotify" in CLIENT_ID:
    print("ERROR: Please set your SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET in the .env file!")
    exit(1)

# Initialize Spotipy
# pyrefly: ignore [unknown-name]
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID, 
    client_secret=CLIENT_SECRET
))

GENRES = ['afrobeats', 'highlife', 'fuji', 'amapiano', 'afropop', 'hip-hop', 'r&b', 'gospel', 'alte']
TRACKS_PER_GENRE = 100

def fetch_tracks():
    print("Connecting to Spotify API...")
    data = []
    
    for genre in GENRES:
        print(f"Fetching tracks for genre: {genre}...")
        # Search for playlists or tracks for this genre
        results = sp.search(q=f'genre:{genre} OR {genre}', type='track', limit=50)
        tracks = results['tracks']['items']
        
        # If we need more, we can paginate, but for a sample, 50-100 per genre is fine.
        # Let's get the next 50 if needed
        if len(tracks) < TRACKS_PER_GENRE:
            try:
                results2 = sp.next(results['tracks'])
                if results2 and 'items' in results2:
                    tracks.extend(results2['items'])
            except Exception as e:
                pass
                
        # Limit to TRACKS_PER_GENRE
        tracks = tracks[:TRACKS_PER_GENRE]
        
        # Get audio features in batches of 100
        track_ids = [t['id'] for t in tracks if t and t.get('id')]
        
        if not track_ids:
            continue
            
        features = sp.audio_features(track_ids)
        
        for i, track in enumerate(tracks):
            if not track or not features[i]:
                continue
                
            f = features[i]
            
            # Use preview_url if available, otherwise it will be None
            preview_url = track.get('preview_url')
            
            data.append({
                'track_id': track['id'],
                'track_name': track['name'],
                'artists': ', '.join([a['name'] for a in track['artists']]),
                'album_name': track['album']['name'],
                'track_genre': genre,
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms'],
                'danceability': f.get('danceability', 0.5),
                'energy': f.get('energy', 0.5),
                'key': f.get('key', 0),
                'loudness': f.get('loudness', -5.0),
                'mode': f.get('mode', 1),
                'speechiness': f.get('speechiness', 0.1),
                'acousticness': f.get('acousticness', 0.2),
                'instrumentalness': f.get('instrumentalness', 0.0),
                'liveness': f.get('liveness', 0.1),
                'valence': f.get('valence', 0.5),
                'tempo': f.get('tempo', 120.0),
                'time_signature': f.get('time_signature', 4),
                'preview_url': preview_url
            })
        
        # Sleep slightly to avoid hitting rate limits
        time.sleep(1)
        
    df = pd.DataFrame(data)
    
    # Drop duplicates in case a track matched multiple genres
    df = df.drop_duplicates(subset=['track_id'])
    
    # Optional: Filter out tracks without a preview_url so everything in our app is playable
    # df = df[df['preview_url'].notna()]
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/spotify_tracks_clean.csv', index=False)
    print(f"Success! Saved {len(df)} real Spotify tracks to data/spotify_tracks_clean.csv")
    
    # Tell user how many are playable
    playable = df['preview_url'].notna().sum()
    print(f"Note: {playable} tracks have 30-second audio previews available.")

if __name__ == "__main__":
    fetch_tracks()
