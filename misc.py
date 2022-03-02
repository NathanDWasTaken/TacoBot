import os, time, json, re, pickle

import spotipy
from spotipy.oauth2     import SpotifyOAuth
from discord.message    import Message

from enums              import WebsiteType
import config


# ---------------------------------- JSON ----------------------------------


def load_json(filename, default_return=None):
    if default_return is None:
        default_return = {}
        
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        try:
            raise default_return
        except TypeError:
            return default_return



def save_json(filename, data):
    path = os.path.split(filename)[0]

    if not os.path.exists(path):
        os.makedirs(path)

    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


# ---------------------------------- MISC ----------------------------------

def parse_url(txt):
    matched_url = re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", txt)

    if matched_url:
        return matched_url.group(0)


def add_values(d: dict, keys: list, value):
    """
    Recursively adds nested dictionaries using the given keys and value
    """

    key = keys.pop(0)


    # Base case, when we've gone over all keys we return
    if len(keys) == 0:
        # If there is not yet an entry for this key we simply make add the key value pair
        if key not in d:
            d[key] = value

        # However if the key is already in the dictionary, we check whether the value is a list. If it is a list we can append the current value to it
        elif type(d[key]) == list:

            if type(value) == list:
                d[key] += value
            else:
                d[key].append(value)

        else:
            raise Exception("Unable to insert the value, the entry already exists and is not a list")

        return d


    elif key not in d:
        recursion_result = add_values({}, keys, value)
    
    else:
        recursion_result = add_values(d[key], keys, value)


    d[key] = recursion_result
    return d


# --------------------------------- Pycord ---------------------------------

async def standard_reply(message: Message, text, delete_delay = config.delete_delay, **kwargs):
    """
    The standard reply message for this bot, takes additional arguments for the channel.send method
    """
    await message.channel.send(f"{message.author.mention} {text}", delete_after=delete_delay, **kwargs)


# Stores the last time each user was scolder
last_scold_times = {
    # Key: channel id
    # Value: {
        # Key: user id
        # Value: last time this user was scolded
    # }
}


async def scold_user(message: Message, reply_text, delete=True):
    """
    Tell off the user by warning them and deleting the message
    """
    if delete:
        await message.delete()


    channel_id  = message.channel.id
    user_id     = message.author.id


    if channel_id not in last_scold_times:
        last_scold_times[channel_id] = {}
        

    if user_id not in last_scold_times[channel_id]:
        last_scold_times[channel_id][user_id] = time.time()
    
    # skip if the previous message was sent a short time ago
    elif time.time() - last_scold_times[channel_id][user_id] < config.delete_delay + 1:
        return

    else:
        last_scold_times[channel_id][user_id] = time.time()


    await standard_reply(message, reply_text)



sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id       = config.spotify_client_id,
        client_secret   = config.spotify_key,
        scope           = config.spotify_scopes,
        redirect_uri    = "http://localhost:8040"
    )
)

def get_spotify_title(song):
    artists = song["artists"]

    title = f"{artists[0]['name']} - {song['name']}"

    if len(artists) > 1:
        extra_artists = [artist["name"] for artist in artists[1:]]

        title += " ft. "
        title += ", ".join(extra_artists)

    return title


def get_api_key(testing=False):
    if testing:
        return os.getenv("DISCORD_API_KEY_TEST")

    return os.getenv("DISCORD_API_KEY")


# -------------------------------- Playlists -------------------------------

with open(config.yt_cred_file, "rb") as file:
    _yt_channel = pickle.load(file)


def sp_add_to_playlist(songID):
    sp.user_playlist_add_tracks(
        user        = config.spotify_client_id, 
        playlist_id = config.spotify_playlist_id, 
        tracks      = [songID]
    )


def yt_add_to_playlist(videoID, playlistID=config.youtube_playlist_id):
    body = {
        'snippet': {
            'playlistId': playlistID, 
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': videoID
            }
        }
    }

    return _yt_channel.playlistItems().insert(
        part="snippet",
        body=body
    ).execute()



def rem_from_playlist(playlistItemID, website: WebsiteType):
    if website == WebsiteType.YouTube:
        _yt_channel.playlistItems().delete(id = playlistItemID).execute()

    elif website == WebsiteType.Spotify:
        sp.playlist_remove_all_occurrences_of_items(
            playlist_id = config.spotify_playlist_id,
            items       = [playlistItemID]
        )


    else:
        print("Invalid Website!")



def fetch_songs_from_playlists(rem_duplicates=True):
    """
    returns playlistItems dict:
        Key:      videoID
        Value:    [WebsiteType, PlaylistItemID]
    """

    # Dict that holds the Song's ID as well as it's Website and PlaylistItemID
    # Key:      videoID
    # Value:    [WebsiteType, PlaylistItemID]
    playlistItems = {}


    # --------------------- YouTube ---------------------
    response        = None
    nextPageToken   = None


    while response is None or nextPageToken:
        response = _yt_channel.playlistItems().list(
            part        ='contentDetails',
            playlistId  = config.youtube_playlist_id,
            maxResults  = 50,
            pageToken   = nextPageToken
        ).execute()


        nextPageToken = response.get('nextPageToken')
    

        for playlistItem in response['items']:
            videoID         = playlistItem["contentDetails"]["videoId"]
            playlistItemID  = playlistItem["id"]

            # If song already in playlistItems that means we have a duplicate -> remove
            if videoID in playlistItems:

                if rem_duplicates:
                    rem_from_playlist(playlistItemID, WebsiteType.YouTube)

                continue

            playlistItems[videoID] = [WebsiteType.YouTube, playlistItemID]


    # --------------------- Spotify ---------------------
    
    sp_next = True
    offset  = 0

    while sp_next is not None:
        tracks = sp.user_playlist_tracks(
            user        = config.spotify_client_id, 
            limit       = config.spotify_request_size,
            playlist_id = config.spotify_playlist_id,
            offset      = offset
        )

        offset += config.spotify_request_size
        sp_next = tracks["next"]


        for item in tracks["items"]:
            trackID = item["track"]["id"]

            if trackID in playlistItems:
                # The track is already in this dict it means there are duplicated -> remove them

                if rem_duplicates:
                    rem_from_playlist(trackID, WebsiteType.Spotify)
                    sp_add_to_playlist(trackID)

                continue

            playlistItems[trackID] = [WebsiteType.Spotify, trackID]


    return playlistItems