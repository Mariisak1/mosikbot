from discord.ext import commands
import discord
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

from dotenv import load_dotenv
import os

from utils.database_manipulation import get_song_recommendations_based_on_mood

## Load environment variables from .env file
load_dotenv()

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    """
    Prints a message in the console when the bot is activated.
    """
    discordChannel = bot.get_channel(CHANNEL_ID)
    await discordChannel.send("Hello, I'm MosikBot! I can recommend you songs based on your mood.")

# this event triggers when a new message is posted in a channel the bot has access to
@bot.event
async def on_message(message):
    """
    Returns a song recommendation (including its corresponding playlist) based on the mood of the message sent by the user.
    Triggers when a new message is posted in a channel the bot has access to.

    Parameters
    ----------
    message : str
        Message sent by the user

    Returns
    -------
    str
        Song recommendation (including its corresponding playlist) based on the mood of the message sent by the user
    """
    if message.author == bot.user:
        return
    if message.content.startswith("!"):
        await bot.process_commands(message)
    else:
        model = AutoModelForSequenceClassification.from_pretrained("sentiment-trainer/checkpoint-6000")
        model.eval()
        tokenizer = AutoTokenizer.from_pretrained("sentiment-trainer/checkpoint-6000")
        sentence = [message.content]
        batch = tokenizer(sentence, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():  
            outputs = model(**batch)
            predictions = torch.softmax(outputs.logits, dim=1)
            label_ids = torch.argmax(predictions, dim=1).tolist()
            if label_ids[0] == 0:
                track = get_song_recommendations_based_on_mood("sad")
                if track:
                    track_name, track_artist, track_url, playlist_url = track
                    response = f"You seem a little sad :cry: \n\nHere's a song that could fit your mood:\n**{track_name} by {track_artist}** \n{track_url} \n\nFrom this playlist: \n{playlist_url}"
                    await message.channel.send(response)
                else:
                    await message.channel.send("I couldn't find any songs that fit your mood, sorry.")
            elif label_ids[0] == 1:
                track = get_song_recommendations_based_on_mood("joy")
                if track:
                    track_name, track_artist, track_url, playlist_url = track
                    response = f"You seem happy :grin: \n\nHere's a song that could fit your mood:\n**{track_name} by {track_artist}** \n{track_url} \n\nFrom this playlist: \n{playlist_url}"
                    await message.channel.send(response)
                else:
                    await message.channel.send("I couldn't find any songs that fit your mood, sorry.")
            elif label_ids[0] == 2:
                track = get_song_recommendations_based_on_mood("love")
                if track:
                    track_name, track_artist, track_url, playlist_url = track
                    response = f"You seem full of love :heart_eyes: \n\nHere's a song that could fit your mood:\n**{track_name} by {track_artist}** \n{track_url} \n\nFrom this playlist: \n{playlist_url}"
                    await message.channel.send(response)
                else:
                    await message.channel.send("I couldn't find any songs that fit your mood, sorry.")
            elif label_ids[0] == 3:
                track = get_song_recommendations_based_on_mood("angry")
                if track:
                    track_name, track_artist, track_url, playlist_url = track
                    response = f"You seem a little irritated :japanese_ogre: \n\nHere's a song that could fit your mood:\n**{track_name} by {track_artist}** \n{track_url} \n\nFrom this playlist: \n{playlist_url}"
                    await message.channel.send(response)
                else:
                    await message.channel.send("I couldn't find any songs that fit your mood, sorry.")
            else: 
                track = get_song_recommendations_based_on_mood("neutral")
                if track:
                    track_name, track_artist, track_url, playlist_url = track
                    response = f"You seem neutral :neutral_face: \n\nHere's a song that could fit your mood:\n**{track_name} by {track_artist}** \n{track_url} \n\nFrom this playlist: \n{playlist_url}"
                    await message.channel.send(response)
                else:
                    await message.channel.send("I couldn't find any songs that fit your mood, sorry.")

# this command returns a song recommendation based on the mood provided
@bot.command(name='song', help='Returns a song recommendation based on your mood. You can choose from: sad, happy, romantic, angry, afraid, surprised')
async def song_recommendation(ctx, mood: str = None):
    """
    Returns a song recommendation based on your mood. You can choose from: sad, happy, romantic, angry, afraid, surprised

    Parameters
    ----------
    ctx : str
        Context of the command
    mood : str
        Mood to base the recommendation on, by default None
    """
    if mood is None:
        await ctx.send("Please provide a mood to base your recommendation on. You can choose from: sad, happy, romantic, angry, afraid, surprised")
        return
    if mood not in ["sad", "happy", "romantic", "angry", "afraid", "surprised"]:
        await ctx.send("Please provide a mood to base your recommendation on. You can choose from: sad, happy, romantic, angry, afraid, surprised")
        return
    track = get_song_recommendations_based_on_mood(mood)
    if track:
        track_name, track_artist, track_url, playlist_url = track
        response = f"Here's a song for you based on your mood: \n**{track_name} by {track_artist}** \n{track_url}"
        await ctx.send(response)
    else:
        await ctx.send("I couldn't find any songs that fit your mood, sorry.")

bot.run(BOT_TOKEN)