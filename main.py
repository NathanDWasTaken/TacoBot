from typing import Dict

from discord        import Message, RawMessageDeleteEvent, TextChannel, Thread
from discord.ext    import commands


from misc           import get_api_key, load_json, parse_url, save_json
from classes        import ThreadChannel, WebsiteType, get_website_type, thread_channels_per_server
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



# Create all ThreadChannel Instances
thread_channels: Dict[int, ThreadChannel] = {}
for channel_list in thread_channels_per_server.values():
    for channel in channel_list:
        channel: TextChannel
        thread_channels[channel.id] = channel



bot = commands.Bot(command_prefix=config.command_prefix, max_messages=2000)


    
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message: Message):
    if message.author == bot.user:
        return


    if message.clean_content.startswith(config.command_prefix):
        handle_command(message)
        return


    if message.channel.id not in thread_channels:
        return


    thread_channel = thread_channels[message.channel.id]

    await thread_channel.moderate_channel(message)


# main purposes of this function:
# - if the message that was deleted has a thread, delete the thread too
# - upldate the local databases of all the shared songs
async def handle_deleted_message(channel_id, msg_id):
    if int(channel_id) not in thread_channels:
        return

    shared_songs_by_songID = load_json(config.shared_songs_by_songID)
    shared_songs_by_msgID  = load_json(config.shared_songs_by_msgID)


    if msg_id in shared_songs_by_msgID:
        song_id = shared_songs_by_msgID[msg_id]


        shared_songs_by_songID[channel_id][song_id].remove(msg_id)
        if shared_songs_by_songID[channel_id][song_id] == []:
            # This means that the song isn't anywhere in the channel anymore
            del shared_songs_by_songID[channel_id][song_id]

            # Which also means we should remove the song from the playlist
            ...

        
        del shared_songs_by_msgID[msg_id]


        save_json(config.shared_songs_by_songID, shared_songs_by_songID)
        save_json(config.shared_songs_by_msgID, shared_songs_by_msgID)


    channel = await bot.fetch_channel(channel_id)
    thread  = channel.get_thread(int(msg_id))
    if type(thread) == Thread:
        await thread.delete()


@bot.event
async def on_raw_message_delete(payload: RawMessageDeleteEvent):
    await handle_deleted_message(str(payload.channel_id), str(payload.message_id))



bot.run(get_api_key(config.testing))