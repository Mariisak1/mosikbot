import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# load environment variables from .env file
load_dotenv()

def get_song_recommendations_based_on_mood(mood):
    """
    Returns a song recommendation (including its corresponding playlist) based on the mood of the message sent by the user

    Parameters
    ----------
    mood : str
        Mood of the message sent by the user

    Returns
    -------
    tuple
        Song recommendation (including its corresponding playlist) based on the mood of the message sent by the user
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            auth_plugin='mysql_native_password'
        )
        cursor = connection.cursor()
        sql = "SELECT name, artist, track_url, playlist_url FROM tracks WHERE mood = %s ORDER BY RAND() LIMIT 1"
        val = (mood,)
        cursor.execute(sql, val)
        result = cursor.fetchone()
        cursor.close()
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return result

# inserts tracks into the database
def insert_tracks_into_db(tracks_info):
    """
    Inserts tracks into the database

    Parameters
    ----------
    tracks_info : list
        List of tracks to be inserted into the database
    """
    counter = 0
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            auth_plugin='mysql_native_password'
        )
        cursor = connection.cursor()
        for track_info in tracks_info:
            sql = "INSERT IGNORE INTO tracks (id, name, artist, playlist_id, valence, energy, danceability, mood, track_url, playlist_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (track_info["id"], track_info["name"], track_info["artist"], track_info["playlist_id"], track_info["valence"], track_info["energy"], track_info["danceability"], track_info["mood"], track_info["track_url"], track_info["playlist_url"])
            cursor.execute(sql, val)
            connection.commit()
            if cursor.rowcount > 0:
                print(cursor.rowcount, "Record inserted.")
            else:
                print("Duplicate record skipped.")
            counter += 1
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print(counter, " records inserted into database.")