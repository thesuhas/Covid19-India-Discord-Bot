import requests
import pandas as pd
import io
import discord
import datetime
from discord.ext import commands, tasks

# Create a bot instance and sets a command prefix
client = commands.Bot(command_prefix = '.')
client.remove_command('help')

# Saving file name
filename = 'states.csv'

# Initialising df to something
df = 0

# Initialising states list
s = list()

@client.event
async def on_ready():
    global df
    global s
    # Start updation loop
    update.start()
    # Create basic data frame and store
    test = requests.get('https://api.covid19india.org/csv/latest/state_wise.csv')
    test = str(test.text)

    data = io.StringIO(test)
    df = pd.read_csv(data, sep=",")
    # Create states list
    s = [df.iloc[i]['State'] for i in range(len(df))]
    # Removing Total and State Unassigned
    s = s[1:len(s) - 1]
    # Making column lower case
    df["State"] = df["State"].str.lower()
    df.to_csv(filename)

@client.command()
async def help(ctx):
    embed = discord.Embed(color = discord.Color.green())
    commands = "`.states` to get a list of states\n`.state {state}` to get cases in that particular state\n`.india` to get nationwide cases"
    embed.add_field(name = 'Commands', value = commands, inline = False)
    await ctx.send(embed = embed)

@client.command()
async def state(ctx, *, state):
    if (state.lower() == "total"):
        await ctx.send("Use `.india` for total cases")
    else:
        entry = df.loc[df['State'] == state.lower()]
        if entry.empty:
            await ctx.send("Chosen state not available")
        else:
            m = f"**Covid Cases in {state[0].upper() + state[1:]}:**\nConfirmed: {entry['Confirmed'].values[0]}\nRecovered: {entry['Recovered'].values[0]}\nDeaths: {entry['Deaths'].values[0]}\nActive: {entry['Active'].values[0]}"
            await ctx.send(m)

@client.command()
async def india(ctx):
    entry = df.loc[df['State'] == 'total']
    m = f"**Covid Cases in the country:**\nConfirmed: {entry['Confirmed'].values[0]}\nRecovered: {entry['Recovered'].values[0]}\nDeaths: {entry['Deaths'].values[0]}\nActive: {entry['Active'].values[0]}"
    await ctx.send(m)

@client.command()
async def states(ctx):
    global s
    # Returns list of states
    string = '**States and Union Territories:\n**'
    for i in s:
        string += i + '\n'
    await ctx.send(string)

# Updates dataframe every 30 mins
@tasks.loop(seconds = 1800)
async def update():
    global df
    # Create basic data frame and store
    test = requests.get('https://api.covid19india.org/csv/latest/state_wise.csv')
    test = str(test.text)

    data = io.StringIO(test)
    df = pd.read_csv(data, sep=",")
    # Making states lowercase
    df["State"] = df["State"].str.lower()
    df.to_csv(filename)
    # Prints when df is last updated
    print("df Updated at: ", datetime.datetime.now())

# Runs the bot
client.run('ODM2NTc4MTI4MzA1NzE3Mjc5.YIgCGA.4ac__Fyd0T_F-0tmx--DStdQaMY')