# Goes over all messages in the given channel and adds all the spotify and youtube songs to the local json files (which is used to keep track of what songs have already been posted)


# Allows us to import files from parent dir
import os, sys

dir = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(dir)

sys.path.append(parent_folder)
# https://stackoverflow.com/questions/16780014/import-file-from-parent-directory


import config
from misc           import _yt_channel
from classes        import MessageType, ShareURL, WebsiteType


from discord        import Message
from discord.ext    import commands
from pytube         import YouTube


bot     = commands.Bot()


if config.testing:
    channel_id = 927704530903261265
else:
    channel_id = 924352019026833498

config.nr_messages


def fetch_songs_from_yt_playlist(pageToken=None, playlistID=config.youtube_playlist_id, maxResults=50):
    return _yt_channel.playlistItems().list(
        part='contentDetails',
        playlistId  = playlistID,
        maxResults  = maxResults,
        pageToken   = pageToken
    ).execute()


def fetch_ids_from_playlists():
    """
    yields videoID and playlistItemID from the different playlists
    """

    # Get all videos from the youtube playlist
    response        = None
    nextPageToken   = None

    while response is None or nextPageToken:
        response = fetch_songs_from_yt_playlist(nextPageToken)

        nextPageToken = response.get('nextPageToken')

    
        for playlistItem in response['items']:
            videoID         = playlistItem["contentDetails"]["videoId"]
            playlistItemID  = playlistItem["id"]

            yield videoID, playlistItemID



for test in fetch_ids_from_playlists():
    print(test)