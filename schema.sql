CREATE TABLE IF NOT EXISTS Users (
    user_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT    NOT NULL UNIQUE,
    password_hash TEXT,
    email      TEXT UNIQUE,
    preferred_genres TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Interactions (
    interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    track_id       TEXT    NOT NULL,
    rating         REAL    CHECK(rating BETWEEN 1 AND 5),
    interacted_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_interactions_user
    ON Interactions(user_id);

CREATE TABLE IF NOT EXISTS Recommendations_Log (
    log_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    session_id   TEXT,
    track_id     TEXT    NOT NULL,
    cb_score     REAL,
    cf_score     REAL,
    alpha_used   REAL,
    hybrid_score REAL,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
