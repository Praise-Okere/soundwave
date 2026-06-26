# Soundwave - Hybrid Music Recommender

Soundwave (formerly NaijaMix) is a music recommendation web application built with Python and Flask. It uses a **Hybrid Recommendation System**, combining both Content-Based filtering and Collaborative Filtering to suggest the best tracks to users based on their preferences and history.

## How It Works

The recommendation engine works in two main steps:

1. **Content-Based Filtering (`models/cb_model.py`)**: 
   When a user requests recommendations based on their favorite genres, the system builds a "User Profile". It then looks at the audio features of the tracks in the database and finds songs that are most similar to the user's preferred genres using cosine similarity. This step generates a large pool of candidate tracks.

2. **Collaborative Filtering (`models/cf_model.py`)**:
   The system trains an SVD (Singular Value Decomposition) model using historical user interaction data (ratings). The SVD model predicts how much the current user would like the candidate tracks based on what similar users have liked.

3. **Hybrid Reranking (`models/hybrid.py`)**:
   The candidate tracks from the Content-Based step are re-ranked using the predictions from the Collaborative Filtering model. A combined score (hybrid score) is calculated, and the top results are returned to the user.

## Project Structure

* `app.py`: The main Flask server application. Handles API routes, database initialization, and connects the UI to the recommendation engine.
* `generate_sample_data.py`: A utility script to generate synthetic music tracks and save them to `data/spotify_tracks_clean.csv`. The models need this data to train!
* `preprocess.py`: Handles loading and normalizing the dataset (scaling audio features) before it goes into the models.
* `schema.sql`: Contains the SQL schema for the SQLite database (`soundwave.db`), which stores users, interactions (ratings), and recommendation logs.
* `models/`:
  * `cb_model.py`: Logic for the Content-Based recommendations.
  * `cf_model.py`: Logic for training the Collaborative Filtering SVD model.
  * `hybrid.py`: Logic for combining CB and CF scores into a final hybrid ranking.
* `templates/` & `static/`: Contains the HTML, CSS, and frontend assets for the web UI.

## Setup & Installation

1. **Install Dependencies**:
   Ensure you have Python installed, then install the required libraries:
   ```bash
   py -m pip install -r requirements.txt
   ```

2. **Generate the Dataset**:
   Before starting the app, you MUST generate the sample track data. Without this, the models will fail to initialize.
   ```bash
   py generate_sample_data.py
   ```

3. **Run the Application**:
   Start the Flask server:
   ```bash
   py app.py
   ```
   The application will be available at `http://127.0.0.1:5000`.

## Features

- **Personalized Recommendations**: Input your favorite genres to get a curated list of tracks.
- **Rating System**: Rate the tracks you are recommended. These ratings are saved in the database to improve future collaborative filtering predictions.
- **Interaction History**: View your past ratings and previous recommendations.
