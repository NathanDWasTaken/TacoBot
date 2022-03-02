# Goes over all messages in the given channel and adds all the spotify and youtube songs to the local json files (which is used to keep track of what songs have already been posted)


# Allows us to import files from parent dir
import os, sys

dir = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(dir)

sys.path.append(parent_folder)
# https://stackoverflow.com/questions/16780014/import-file-from-parent-directory


import config
from misc           import get_api_key, parse_url, load_json, save_json, add_values, sp_add_to_playlist, yt_add_to_playlist, rem_from_playlist, fetch_songs_from_playlists, sp
from classes        import MessageType, ShareURL, WebsiteType


from discord        import Message
from discord.ext    import commands
from pytube         import YouTube


bot     = commands.Bot()


if config.testing:
    channel_id = "927704530903261265"
else:
    channel_id = "924352019026833498"


    
@bot.event
async def on_ready():

    # --------------------------- SYNC MESSAGES ---------------------------
    # This part of the code goes through all messages in the channel and adds the songs to the local database here as well as the playlists (currently only youtube)

    shared_songs_by_songID      = load_json(config.shared_songs_by_songID)
    shared_songs_by_msgID       = load_json(config.shared_songs_by_msgID)
    playlist_items_by_songID    = load_json(config.playlist_items_by_songID)

    # Keep all entries except the ones from the channel we're updating
    for d in [shared_songs_by_songID, shared_songs_by_msgID, playlist_items_by_songID]:
        if channel_id in d:
            d[channel_id] = {}


    # All the songs that are in the different playlists (YouTube, Spotify)
    playlist_songs = fetch_songs_from_playlists()


    share_edm = bot.get_channel(int(channel_id))
    messages = await share_edm.history(limit=config.nr_messages).flatten()

    print()
    print(f"Found {len(messages)}/{config.nr_messages} messages in '{share_edm.name}'")
    print()


    for message in messages:
        message: Message
        msg_id = str(message.id)


        # --------------- SYNC LOCAL DATABASE TO MESSAGE ---------------
        url = parse_url(message.clean_content)

        if url is None:
            print(f"Message does not contain url: '{message.clean_content}'")
            continue

        share_msg   = ShareURL(url)
        website     = share_msg.website

        if msg_id not in shared_songs_by_msgID[channel_id]:
            if share_msg.message_type == MessageType.InvalidUrl:
                print(f"Could not ID the following url: '{share_msg.url}'")
                continue


            # Get song ID and add the song to the local databases

            if website == WebsiteType.YouTube:
                song_id = YouTube(url).video_id


            elif website == WebsiteType.Spotify:
                song_id = sp.track(url)["id"]


            else:
                print("Invalid website! Can't get necessary ID!")
                continue


            add_values(shared_songs_by_songID, [channel_id, song_id], [msg_id])
            add_values(shared_songs_by_msgID, [channel_id, msg_id], song_id)

        else:
            song_id = shared_songs_by_msgID[channel_id][msg_id]
            print("This message is already in the 'shared_songs_by_msgID.json' database!")


        # --------------- SYNC REMOVE PLAYLIST TO MESSAGE ---------------
        if song_id not in playlist_items_by_songID or song_id not in playlist_songs:

            # If the song is already in a playlist we fetch the playlistItemID here
            if song_id in playlist_songs:
                playlistItemID = playlist_songs[song_id][1]
            

            # If it isn't we add it
            else:
                if website == WebsiteType.YouTube:
                    playlistItemID = yt_add_to_playlist(song_id)["id"]
                
                elif website == WebsiteType.Spotify:
                    sp_add_to_playlist(song_id)
                    playlistItemID = song_id


                else:
                    print("Can't add song to playlist from this website!")
                    continue


                playlist_songs[song_id]         = [website.value, playlistItemID]

            add_values(playlist_items_by_songID, [channel_id, song_id], [website.value, playlistItemID])

        else:
            print("Song Already in Playlist!")



    save_json(config.shared_songs_by_songID, shared_songs_by_songID)
    save_json(config.shared_songs_by_msgID, shared_songs_by_msgID)
    save_json(config.playlist_items_by_songID, playlist_items_by_songID)



    # --------------------------- REMOVE EXCESS SONGS FROM PLAYLIST ---------------------------
    # This part of the code goes through all songs in a playlist and makes sure those songs are still posted at least once in the channel
    # If there is no message with the song, the song is removed from the playlist

    for videoID, (website, playlistItemID) in playlist_songs.items():
        if not videoID in playlist_items_by_songID[channel_id]:
            rem_from_playlist(playlistItemID, website=website)


    print(f'We have logged in as {bot.user}')


    bot.loop.stop()
    




bot.run(get_api_key(config.testing))