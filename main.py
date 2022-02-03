from typing import Dict

from discord        import Message, TextChannel, Thread
from discord.ext    import commands


from misc           import get_api_key, load_json, parse_url, save_json
from classes        import ThreadChannel, get_website_type, thread_channels_per_server
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



bot     = commands.Bot(command_prefix=config.command_prefix)


    
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




# main purpose of this function is to delete thread if the thread's message was deleted
@bot.event
async def on_message_delete(message: Message):
    if message.author == bot.user:
        return

    if message.channel.id not in thread_channels:
        return

    shared_songs = load_json(config.shared_songs_file)

    msg_id = str(message.id)

    if msg_id in shared_songs[message.channel.id]:
        del shared_songs[message.channel.id][msg_id]

    save_json(config.shared_songs_file, shared_songs)


    thread = message.channel.get_thread(message.id)
    if type(thread) == Thread:
        await thread.delete()


bot.run(get_api_key(config.testing))