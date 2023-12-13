from dotenv import load_dotenv
import os
import base64
import json
import time
from requests import post, get
from utils.database_manipulation import insert_tracks_into_db

# load environment variables from .env file
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# returns an access token from spotify which lasts for 1 hour, used to make requests to the spotify api
def get_token():
    """
    Returns an access token from spotify which lasts for 1 hour, used to make requests to the spotify api

    Returns
    -------
    str
        Spotify API access token
    """
    auth_string = SPOTIFY_CLIENT_ID + ":" + SPOTIFY_CLIENT_SECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

# gets the authorization header for spotify api requests
def get_auth_header(token):
    """
    Returns the authorization header for spotify api requests

    Parameters
    ----------
    token : str
        Spotify API access token
    
    Returns
    -------
    dict
        Authorization header
    """
    return {
        "Authorization": "Bearer " + token
    }

# returns features playlist ids from spotify api
def get_featured_playlists_ids(token):
    """
    Fetches featured playlists ids from spotify

    Parameters
    ----------
    token : str
        Spotify API access token
    
    Returns
    -------
    list
        List of playlist ids
    """
    url = "https://api.spotify.com/v1/browse/featured-playlists"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    playlists = json_result["playlists"]["items"]
    playlist_ids = [playlist["id"] for playlist in playlists]
    time.sleep(60)
    return playlist_ids

# returns random tracks from a list of playlists
def get_tracks_from_playlists(token, playlist_ids):
    """
    Fetches tracks from a list of playlists

    Parameters
    ----------
    token : str
        Spotify API access token
    playlist_ids : list
        List of playlist ids

    Returns
    -------
    list
        List of tracks from the playlists
    """
    url = "https://api.spotify.com/v1/playlists/"
    headers = get_auth_header(token)

    tracks_info = []
    for playlist_id in playlist_ids:
        query_url = url + playlist_id + "/tracks?limit=100"
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)

        for item in json_result["items"]:
            track = item["track"]
            track_info = {
                "id": track["id"],
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "playlist_id": playlist_id,
                "track_url": track["external_urls"]["spotify"],
                "playlist_url": "https://open.spotify.com/playlist/" + playlist_id
            }
            tracks_info.append(track_info)
    time.sleep(60)
    return tracks_info

# returns extended tracks (with audio features and mood) from a list of tracks
def get_track_info(token, tracks, min, max):
    """
    Fetches and returns extended tracks (with audio features and mood) from a list of tracks

    Parameters
    ----------
    token : str
        Spotify API access token
    tracks : list
        List of tracks
    min : int
        Minimum index of the tracks list
    max : int
        Maximum index of the tracks list

    Returns
    -------
    list
        List of extended tracks (including audio features and mood)
    """
    url = "https://api.spotify.com/v1/audio-features/"
    headers = get_auth_header(token)

    # query several tracks at once, limit is 50 tracks according to spotify docs
    query = "?ids=" + ",".join([track["id"] for track in tracks[min:max]])
    query_url = url + query
    result = get(query_url, headers=headers)

    json_result = json.loads(result.content)

    print("STATUS CODE: " + str(result.status_code))

    track_features_list = json_result["audio_features"]

    tracks_info = []
    for track, track_features in zip(tracks[min:max], track_features_list):

        if not track_features:
            continue

        if track_features["valence"] > 0.6 and track_features["energy"] > 0.6:
            mood = "joy"
        elif track_features["valence"] < 0.4 and track_features["energy"] < 0.4:
            mood = "sad"
        elif track_features["valence"] < 0.4 and track_features["energy"] > 0.6:
            mood = "angry"
        elif track_features["valence"] >= 0.4 and track_features["valence"] <= 0.6 and track_features["energy"] >= 0.4 and track_features["energy"] <= 0.6:
            mood = "love"
        else:
            mood = "neutral"

        tracks_features = {
            "id": track["id"],
            "name": track["name"],
            "artist": track["artist"],
            "playlist_id": track["playlist_id"],
            "valence": track_features["valence"],
            "energy": track_features["energy"],
            "danceability": track_features["danceability"],
            "mood": mood,
            "track_url": track["track_url"],
            "playlist_url": track["playlist_url"]
        }
        print(tracks_features)
        tracks_info.append(tracks_features)
    return tracks_info

# retrieves access token
token = get_token()

# retrieves featured playlists ids
playlist_ids = get_featured_playlists_ids(token)

# retrieves tracks from playlists
tracks = get_tracks_from_playlists(token, playlist_ids)

# retrieves extended tracks (with audio features and mood), spotify only allows 50 tracks per request
counter = 0
while(counter <= len(tracks)):
    counter += 50
    token2 = get_token()
    tracks_extended = get_track_info(token2, tracks, min=counter, max=counter+50)
    insert_tracks_into_db(tracks_extended)
    time.sleep(300)
