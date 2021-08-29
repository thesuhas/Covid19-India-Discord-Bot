# import discord
# from discord.ext import commands
# from discord_slash import SlashCommand
# import os
# from dotenv import load_dotenv

# Create a bot instance and sets a command prefix
client = commands.Bot(command_prefix='.', intents=discord.Intents.all())
client.remove_command('help')
slash = SlashCommand(client, sync_commands = True, sync_on_cog_reload = True)

# load the env variable token
load_dotenv()

# Load the cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f"cogs.{filename[:-3]}")

# Runs the bot
client.run(os.getenv('TOKEN'))
