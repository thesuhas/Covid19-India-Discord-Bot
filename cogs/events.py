import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        # Create embed to send
        embed = discord.Embed(color=discord.Color.green(), title="Covid19 India Bot",
                            description="Gives various statistics regarding Covid19 in India along with vaccination slots near you")
        embed.add_field(
            name="Hello!", value="Thank you for adding the bot to your server! Use `.help` to find out what commands it currently supports!")
        alerts_embed = discord.Embed(
            color=discord.Color.green(), title="IMPORTANT")
        alerts_embed.add_field(
            name="\u200b", value="Members with the `Manage Server` permissions are requested to run `.alerts {channel_name}` command to receive important updates from the developers")

        for channels in guild.text_channels:
            if channels.permissions_for(guild.me).send_messages:
                await channels.send(embed=embed)
                await channels.send(embed=alerts_embed)
                break
        ownerObj = guild.owner
        try:
            await ownerObj.send("Thank you for adding me to your server! It is important that you run the `.alerts {channel.name}` command so that you get important updates from the developers.\nIf you have any questions or queries, you can mail us at covidindiabot@gmail.com")
        except:
            pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        dat = ''
        fp = open('alerts.csv', 'r')
        for line1 in fp:
            if(str(guild.id) not in line1.split(',')):
                dat += line1
        fp.close()
        fp = open('alerts.csv', 'w')
        fp.write(dat)
        fp.close()

        dat = ''
        fp = open('mypings.csv', 'r')
        for line in fp:
            if(str(guild.id) in line.split(',')[1]):
                continue
            dat += line
        fp.close()
        fp = open('mypings.csv', 'w')
        fp.write(dat)
        fp.close()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            if((message.channel.id == 840644400564142111) and (message.author.id == 836578128305717279)):
                await message.publish()
            else:
                pass
        elif (('<@!836578128305717279>' in message.content) or ('<@836578128305717279>' in message.content)):
            await message.channel.send(f"{message.author.mention} my prefix in this server is `.`\nUse `.help` to know what all I can do")
        else:
            await self.client.process_commands(message)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        dat =''
        fp = open('mypings.csv', 'r')
        for line in fp:
            if((str(member.guild.id) in line.split(',')[1]) and (str(member.id) in line.split(',')[0])):
                continue
            dat += line
        fp.close()
        fp = open('mypings.csv', 'w')
        fp.write(dat)
        fp.close()


def setup(client):
    client.add_cog(Events(client))