from typing import Dict

from discord        import Message, Thread
from discord.ext    import commands


from misc           import get_api_key
from classes        import ThreadChannel, thread_channels_per_server
import config




bot     = commands.Bot(command_prefix=config.command_prefix)



thread_channels: Dict[int, ThreadChannel] = {}
for channel_list in thread_channels_per_server.values():
    for channel in channel_list:
        thread_channels[channel.id] = channel



    
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')



@bot.event
async def on_message(message: Message):
    if message.author == bot.user:
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


    thread = message.channel.get_thread(message.id)
    if type(thread) == Thread:
        await thread.delete()


bot.run(get_api_key(config.testing))