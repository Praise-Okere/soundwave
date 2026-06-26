import os
import sqlite3
# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, jsonify
import pandas as pd

from preprocess import load_and_clean
from models.cb_model import build_user_profile, get_cb_recommendations
from models.cf_model import generate_synthetic_interactions, train_svd
from models.hybrid import hybrid_recommend

app = Flask(__name__)
# Vercel has a read-only filesystem, so we use /tmp for the SQLite DB when deployed
DB_FILE = "/tmp/soundwave.db" if os.environ.get("VERCEL") else "soundwave.db"
DATA_FILE = "data/spotify_tracks_clean.csv"

# Globals for models
DF_CLEAN = None
SCALER = None
CF_MODEL = None

def init_db():
    if not os.path.exists(DB_FILE):
        print("Initializing database...")
        conn = sqlite3.connect(DB_FILE)
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.close()

def init_models():
    global DF_CLEAN, SCALER, CF_MODEL
    print("Loading data and initializing models...")
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found. Please run generate_sample_data.py first.")
        return
    
    DF_CLEAN, SCALER = load_and_clean(DATA_FILE)
    
    # Generate synthetic interactions and train SVD
    print("Training collaborative filtering model...")
    interactions_df = generate_synthetic_interactions(DF_CLEAN, num_users=500)
    CF_MODEL = train_svd(interactions_df)
    print("Models initialized successfully.")

# Initialize on startup
with app.app_context():
    init_db()
    init_models()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/discover')
def discover():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    if DF_CLEAN is None or CF_MODEL is None:
        return jsonify({"error": "Models not initialized."}), 500
        
    data = request.json
    if not data or 'genres' not in data:
        return jsonify({"error": "Missing genres in request body."}), 400
        
    liked_genres = data['genres']
    if not isinstance(liked_genres, list) or len(liked_genres) == 0:
        return jsonify({"error": "Genres must be a non-empty list."}), 400
        
    user_id = data.get('user_id', 'guest')
    
    # 1. Content-Based Profile & Candidates
    user_profile = build_user_profile(DF_CLEAN, liked_genres)
    cb_candidates = get_cb_recommendations(DF_CLEAN, user_profile, top_n=50)
    
    # 2. Hybrid Reranking
    recommendations = hybrid_recommend(DF_CLEAN, cb_candidates, CF_MODEL, user_id, top_n=10)
    
    # Log to DB
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Ensure user exists for logging
        cursor.execute("INSERT OR IGNORE INTO Users (username) VALUES (?)", (str(user_id),))
        
        # We need the numeric user_id from the DB for logging
        cursor.execute("SELECT user_id FROM Users WHERE username = ?", (str(user_id),))
        row = cursor.fetchone()
        if row:
            numeric_user_id = row[0]
            for rec in recommendations:
                cursor.execute("""
                    INSERT INTO Recommendations_Log 
                    (user_id, track_id, cb_score, cf_score, alpha_used, hybrid_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    numeric_user_id, 
                    rec['track_id'], 
                    rec['cb_score'], 
                    rec['cf_score'], 
                    0.6, # ALPHA
                    rec['hybrid_score']
                ))
            conn.commit()
    except Exception as e:
        print(f"Error logging recommendations: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            
    return jsonify({"recommendations": recommendations})

@app.route('/rate', methods=['POST'])
def rate():
    data = request.json
    if not data or 'track_id' not in data or 'rating' not in data:
        return jsonify({"error": "Missing required fields."}), 400
        
    user_id = data.get('user_id', 'guest')
    track_id = data['track_id']
    try:
        rating = float(data['rating'])
    except ValueError:
        return jsonify({"error": "Rating must be a number."}), 400
        
    if not (1 <= rating <= 5):
        return jsonify({"error": "Rating must be between 1 and 5."}), 400
        
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Users (username) VALUES (?)", (str(user_id),))
        cursor.execute("SELECT user_id FROM Users WHERE username = ?", (str(user_id),))
        row = cursor.fetchone()
        if row:
            numeric_user_id = row[0]
            cursor.execute("""
                INSERT INTO Interactions (user_id, track_id, rating)
                VALUES (?, ?, ?)
            """, (numeric_user_id, track_id, rating))
            conn.commit()
            
            # Note: Retraining SVD live on every rating is out of scope for v1.
            # Periodic retraining would be a production improvement.
            return jsonify({"success": True})
        return jsonify({"error": "User not found."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/history/<user_id>', methods=['GET'])
def history(user_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT user_id FROM Users WHERE username = ?", (str(user_id),))
        row = cursor.fetchone()
        if not row:
            return jsonify({"history": [], "interactions": []})
            
        numeric_user_id = row[0]
        
        cursor.execute("""
            SELECT track_id, rating, interacted_at 
            FROM Interactions 
            WHERE user_id = ? 
            ORDER BY interacted_at DESC LIMIT 50
        """, (numeric_user_id,))
        interactions = [dict(ix) for ix in cursor.fetchall()]
        
        cursor.execute("""
            SELECT track_id, hybrid_score, generated_at 
            FROM Recommendations_Log 
            WHERE user_id = ? 
            ORDER BY generated_at DESC LIMIT 50
        """, (numeric_user_id,))
        recommendations = [dict(r) for r in cursor.fetchall()]
        
        return jsonify({
            "interactions": interactions,
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
