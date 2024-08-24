import requests, base64, os

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

def get_token():
    auth_str = f'{client_id}:{client_secret}'
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    headers = {
        'Authorization': f'Basic {b64_auth_str}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}

    response = requests.post(
        'https://accounts.spotify.com/api/token', 
        headers = headers, 
        data = data
        )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}, Response: {response.text}")
        response.raise_for_status()
    
    return response.json().get('access_token')

def search_song(query):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'q': query,
        'type': 'track',
        'limit': 5
    }

    response = requests.get(
        'https://api.spotify.com/v1/search', 
        headers = headers, 
        params = params
        )
    
    results = response.json().get('tracks', {}).get('items', [])

    return results

def get_audio_features(track_id):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}

    response = requests.get(
        f'https://api.spotify.com/v1/audio-features/{track_id}',
        headers = headers
    )

    return response.json()

def key_mode_to_camelot(key, mode):
    camelot_map = {
        (0, 1): "8B", (0, 0): "5A", (1, 1): "3B", (1, 0): "12A",
        (2, 1): "10B", (2, 0): "7A", (3, 1): "5B", (3, 0): "2A",
        (4, 1): "12B", (4, 0): "9A", (5, 1): "7B", (5, 0): "4A",
        (6, 1): "2B", (6, 0): "11A", (7, 1): "9B", (7, 0): "6A",
        (8, 1): "4B", (8, 0): "1A", (9, 1): "11B", (9, 0): "8A",
        (10, 1): "6B", (10, 0): "3A", (11, 1): "1B", (11, 0): "10A"
    }
    return camelot_map[(key, mode)]

def get_camelot_neighbors(camelot_key):
    camelot_neighbors = {
        "1A": ["12A", "2A", "1B"], "2A": ["1A", "3A", "2B"], "3A": ["2A", "4A", "3B"],
        "4A": ["3A", "5A", "4B"], "5A": ["4A", "6A", "5B"], "6A": ["5A", "7A", "6B"],
        "7A": ["6A", "8A", "7B"], "8A": ["7A", "9A", "8B"], "9A": ["8A", "10A", "9B"],
        "10A": ["9A", "11A", "10B"], "11A": ["10A", "12A", "11B"], "12A": ["11A", "1A", "12B"],
        "1B": ["12B", "2B", "1A"], "2B": ["1B", "3B", "2A"], "3B": ["2B", "4B", "3A"],
        "4B": ["3B", "5B", "4A"], "5B": ["4B", "6B", "5A"], "6B": ["5B", "7B", "6A"],
        "7B": ["6B", "8B", "7A"], "8B": ["7B", "9B", "8A"], "9B": ["8B", "10B", "9A"],
        "10B": ["9B", "11B", "10A"], "11B": ["10B", "12B", "11A"], "12B": ["11B", "1B", "12A"]
    }

    return camelot_neighbors[camelot_key]

def get_artist_genres(artist_id):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'https://api.spotify.com/v1/artists/{artist_id}',
        headers = headers
    )
    artist_data = response.json()
    return artist_data.get('genres', [])

def get_recommendations(seed_track_id, seed_audio_features):
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    params = {
        'seed_tracks': seed_track_id,
        'limit': 20, 
        'target_tempo': seed_audio_features['tempo'],
        'target_energy': seed_audio_features['energy']
    }

    response = requests.get(
        'https://api.spotify.com/v1/recommendations',
        headers = headers,
        params = params
    )

    recommended_tracks = response.json().get('tracks', [])
    seed_key = seed_audio_features['key']
    seed_mode = seed_audio_features['mode']
    seed_camelot = key_mode_to_camelot(seed_key, seed_mode)
    camelot_neighbors = get_camelot_neighbors(seed_camelot)

    recommendations = []
    for track in recommended_tracks:
        track_features = get_audio_features(track['id'])
        track_camelot = key_mode_to_camelot(track_features['key'], track_features['mode'])
        print(f"Checking track: {track['name']} - BPM: {track_features['tempo']}, Camelot: {track_camelot}, Energy: {track_features['energy']}")
        if seed_camelot == track_camelot or track_camelot in camelot_neighbors:
            if abs(track_features['tempo'] - seed_audio_features['tempo']) <= 10:
                if abs(track_features['energy'] - seed_audio_features['energy']) <= 0.2:
                    artist_id = track['artists'][0]['id']
                    track_genres = ', '.join(get_artist_genres(artist_id))
                    if track['id'] !=seed_track_id:
                        recommendations.append({
                            'track': track,
                            'track_features': track_features,
                            'genres': track_genres
                        })
                        print(f"Added {track['name']} to recommendations with genres: {track_genres}")
        else:
            print(f"Excluded {track['name']} due to Camelot key mismatch.")

    return recommendations[:3]