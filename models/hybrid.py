from models.cf_model import get_cf_score

ALPHA = 0.6   # weight assigned to content-based score

def hybrid_recommend(df, cb_recs, cf_model, user_id, top_n=10):
    results = []
    for _, row in cb_recs.iterrows():
        cb = row['cb_score']
        cf = get_cf_score(cf_model, user_id, row['track_id'])
        hybrid_score = ALPHA * cb + (1 - ALPHA) * cf
        results.append({
            'track_id': row['track_id'],
            'track_name': row['track_name'],
            'artists': row['artists'],
            'track_genre': row['track_genre'],
            'preview_url': row.get('preview_url', None),
            'cb_score': round(float(cb), 4),
            'cf_score': round(float(cf), 4),
            'hybrid_score': round(float(hybrid_score), 4)
        })
    results.sort(key=lambda x: x['hybrid_score'], reverse=True)
    return results[:top_n]
