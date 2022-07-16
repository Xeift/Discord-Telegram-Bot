import requests
import json
import asyncio
import os
import json
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands
from telegram import Update
from telegram.ext import Updater,CallbackContext,MessageHandler,Filters
from telegram.utils import helpers
from telegram.ext.dispatcher import run_async

load_dotenv('token.env')
discordToken = os.getenv('DCTOKEN')# discord bot token
telegramToken = os.getenv('TGTOKEN')# telegram bot token
discordChannelId = os.getenv('DCCID')# discord announcement channel id
loop = asyncio.get_event_loop()

#--------------------------------------------------------------------------------------------------------------
bot = commands.Bot(
	command_prefix="k!",
	case_insensitive=True,
  	intents=discord.Intents.all(),
  	help_command=None
)

async def sendDcAnnouncement(textUpdate,nonTextUpdate):
    announcementChannel = bot.get_channel(int(discordChannelId))
    if textUpdate != None and nonTextUpdate != None:
        await announcementChannel.send(textUpdate,file=discord.File(nonTextUpdate))
        os.remove(nonTextUpdate)
    elif textUpdate == None:
        await announcementChannel.send(file=discord.File(nonTextUpdate))
        os.remove(nonTextUpdate)
    elif nonTextUpdate == None:
        await announcementChannel.send(textUpdate)

def getTgAnnouncement(update: Update, context: CallbackContext):
    textUpdate = None
    nonTextUpdate = None
    updateType = helpers.effective_message_type(update)

    if updateType == 'text':
        textUpdate = update.channel_post.text
    else:
        textUpdate = update.channel_post.caption
        if updateType == 'photo':
            nonTextUpdate = update.channel_post.photo[-1].get_file()['file_path']
        elif updateType == 'video':
            nonTextUpdate = update.channel_post.video.get_file()['file_path']     
        elif updateType == 'document':
            nonTextUpdate = update.channel_post.document.get_file()['file_path']
        elif updateType == 'voice':
            nonTextUpdate = update.channel_post.voice.get_file()['file_path']
    loop.create_task(sendDcAnnouncement(textUpdate,nonTextUpdate))

@bot.event
async def on_ready():
    print(f'logged in as {bot.user}')
    updater = Updater(token=telegramToken,use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    getTgAnnouncement_handler = MessageHandler((~Filters.command),getTgAnnouncement)
    dispatcher.add_handler(getTgAnnouncement_handler)
    updater.start_polling()

bot.run(discordToken)
#--------------------------------------------------------------------------------------------------------------