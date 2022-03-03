from typing import Dict

from discord        import Message, RawMessageDeleteEvent, TextChannel, Thread
from discord.ext    import commands


from misc           import get_api_key, load_json, save_json, rem_from_playlist
from misc           import fetch_songs_from_playlists, rem_from_playlist
from classes        import ShareMedia, SharePics, ShareSuggestion, ThreadChannel, WebsiteType, thread_channels
import config



def test_bot():
    """
    Run an automated test of the bot in the channel
    """
    # TODO
    pass


def handle_command(message: Message):
    text = message.clean_content.replace(config.command_prefix, "")

    command = text.split()[0]
    if command == "test":
        if message.guild.id == config.test_server_id:
            test_bot()


    # send back Invalid command message



bot = commands.Bot(command_prefix=config.command_prefix, max_messages=2000)

    
@bot.event
async def on_ready():
    channel         = bot.get_channel(int(config.playlist_channel))

    
    channel_id      = str(channel.id)
    thread_channel: ThreadChannel = thread_channels[channel.id]
    
    # --------------------------- SYNC MESSAGES ---------------------------
    # This part of the code goes through all messages in the channel and adds the songs to the local database here as well as the playlists (currently only youtube)

    shared_songs_by_songID      = load_json(config.shared_songs_by_songID)
    shared_songs_by_msgID       = load_json(config.shared_songs_by_msgID)
    playlist_items_by_songID    = load_json(config.playlist_items_by_songID)

    # Keep all entries except the ones from the channel we're updating
    for d in [shared_songs_by_songID, shared_songs_by_msgID, playlist_items_by_songID]:
        d[channel_id] = {}

    save_json(config.shared_songs_by_songID, shared_songs_by_songID)
    save_json(config.shared_songs_by_msgID, shared_songs_by_msgID)
    save_json(config.playlist_items_by_songID, playlist_items_by_songID)


    # All the songs that are in the different playlists (YouTube, Spotify)
    playlist_songs = fetch_songs_from_playlists()


    messages = await channel.history(limit=config.nr_messages).flatten()

    print()
    print(f"Found {len(messages)}/{config.nr_messages} messages in '{channel.name}'")
    print()


    for message in messages:
        await thread_channel.moderate_channel(message, syncing=True)



    # --------------------------- REMOVE EXCESS SONGS FROM PLAYLIST ---------------------------
    # This part of the code goes through all songs in a playlist and makes sure those songs are still posted at least once in the channel
    # If there is no message with the song, the song is removed from the playlist

    for videoID, (website, playlistItemID) in playlist_songs.items():
        if not videoID in playlist_items_by_songID[channel_id]:
            rem_from_playlist(website, playlistItemID, videoID)


    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message: Message):
    if message.author == bot.user:
        if message.is_system() and message.type.name == "thread_created" and message.channel.id in thread_channels:
            await message.delete()

        return


    if message.clean_content.startswith(config.command_prefix):
        handle_command(message)
        return


    if message.channel.id not in thread_channels:
        return


    thread_channel: ThreadChannel = thread_channels[message.channel.id]

    await thread_channel.moderate_channel(message)



# main purposes of this function:
# - if the message that was deleted has a thread, delete the thread too
# - upldate the local databases of all the shared songs
@bot.event
async def on_raw_message_delete(payload: RawMessageDeleteEvent):
    channel_id  = str(payload.channel_id)
    msg_id      = str(payload.message_id)

    if int(channel_id) not in thread_channels:
        return

    shared_songs_by_songID = load_json(config.shared_songs_by_songID)
    shared_songs_by_msgID  = load_json(config.shared_songs_by_msgID)

    if msg_id in shared_songs_by_msgID[channel_id]:
        song_id = shared_songs_by_msgID[channel_id][msg_id]

        shared_songs_by_songID[channel_id][song_id].remove(msg_id)

        # The song isn't anywhere in the channel anymore
        if shared_songs_by_songID[channel_id][song_id] == []:

            playlist_items_by_songID = load_json(config.playlist_items_by_songID)

            # Which also means we should remove the song from the playlist
            website_name, playlistItemID = playlist_items_by_songID[channel_id][song_id]
            website = WebsiteType(website_name)

            rem_from_playlist(website, playlistItemID, song_id)

            del shared_songs_by_songID[channel_id][song_id]
            del playlist_items_by_songID[channel_id][song_id]

            save_json(config.playlist_items_by_songID, playlist_items_by_songID)

        del shared_songs_by_msgID[channel_id][msg_id]

        save_json(config.shared_songs_by_songID, shared_songs_by_songID)
        save_json(config.shared_songs_by_msgID, shared_songs_by_msgID)


    channel: TextChannel = await bot.fetch_channel(channel_id)
    thread  = channel.get_thread(int(msg_id))
    if type(thread) == Thread:
        await thread.delete()



bot.run(get_api_key(config.testing))