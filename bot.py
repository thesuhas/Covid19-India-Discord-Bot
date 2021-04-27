import requests
import pandas as pd
import io
import discord
from discord.ext import commands

# Create a bot instance and sets a command prefix
client = commands.Bot(command_prefix = '.')
client.remove_command('help')

# Saving file name
filename = 'states.csv'

# Initialising df to something
df = 0

@client.event
async def on_ready():
    global df
    # Create basic data frame and store
    test = requests.get('https://api.covid19india.org/csv/latest/state_wise.csv')
    test = str(test.text)

    data = io.StringIO(test)
    df = pd.read_csv(data, sep=",")
    df.to_csv(filename)

# Runs the bot
client.run('ODM2NTc4MTI4MzA1NzE3Mjc5.YIgCGA.4ac__Fyd0T_F-0tmx--DStdQaMY')