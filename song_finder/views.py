from django.shortcuts import render
from django.http import JsonResponse
from .spotify import search_song, get_audio_features, get_recommendations, key_mode_to_camelot

def home(request):
    context = {}
    return render(request, 'song_finder/home.html', context)

def song_search(request):
    query = request.GET.get('query', '')
    results = search_song(query)
    data = [
        {
            'id': track['id'],
            'name': track['name'],
            'artists': ', '.join([artist['name'] for artist in track['artists']]),
            'cover_art': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'preview_url': track['preview_url'],
            'genres': ', '.join(track['artists'][0].get('genres', [])) if track['artists'] else ''
        }
        for track in results
    ]
    return JsonResponse(data, safe=False)

def results(request):
    track_id = request.GET.get('track_id')
    print(f"Received track_id: {track_id}")
    if not track_id:
        return render(request, 'song_finder/results.html', {'error': 'No track ID provided.'})
    
    audio_features = get_audio_features(track_id)
    if not audio_features or 'tempo' not in audio_features:
        return render(request, 'song_finder/results.html', {'error': 'No audio features found for the given track or missing required audio features.'})

    print(f"Audio Features: {audio_features}")

    recommendations = get_recommendations(track_id, audio_features)

    recommendation_data = [
        {
            'cover_art': rec['track']['album']['images'][0]['url'] if rec['track']['album']['images'] else None,
            'artist': ', '.join([artist['name'] for artist in rec['track']['artists']]),
            'song': rec['track']['name'],
            'bpm': round(rec['track_features']['tempo']),
            'key': key_mode_to_camelot(rec['track_features']['key'], rec['track_features']['mode']),
            'genre': rec['genres'].split(',')[0].title() if rec['genres'] else 'Unknown',
            'preview_url': rec['track']['preview_url']
        }
        for rec in recommendations
    ]

    context = {'recommendations': recommendation_data}
    return render(request, 'song_finder/results.html', context)
