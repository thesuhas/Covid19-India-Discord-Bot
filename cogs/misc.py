import discord
from discord.ext import commands
from discord_slash import cog_ext
import json
from cogs.helpers import Helpers
from cogs.cowin import Cowin
import subprocess
import sys
class Misc(commands.Cog):
    # Initialisation
    def __init__(self, client):
        self.client = client

        
    @commands.command(aliases=['pull'])
    async def git_pull(self, ctx):
        if((ctx.author.id == 554876169363652620) or (ctx.author.id == 723377619420184668) or (ctx.author.id == 718845827413442692) or (ctx.author.id == 404597472103759872) or (ctx.author.id == 771985293011058708)):   
            await ctx.send("Pulling repo from git")
            sys.stdout.flush()
            p = subprocess.Popen(['git', 'pull'], stdout=subprocess.PIPE)
            for line in iter(p.stdout.readline,''):
                if not line:
                    break
                await ctx.channel.send(str(line.rstrip(), 'utf-8', 'ignore'))
            sys.stdout.flush()
        else:
            await ctx.channel.send("You can't execute this command")
            
    @commands.command(aliases=['restart'])
    async def _restart(self, ctx):
        if((ctx.author.id == 554876169363652620) or (ctx.author.id == 723377619420184668) or (ctx.author.id == 718845827413442692) or (ctx.author.id == 404597472103759872) or (ctx.author.id == 771985293011058708)):   
            await ctx.send("sending files")
            with open('data/alerts.csv', 'r') as fp:
                await self.client.get_channel(841561036305465344).send(file=discord.File(fp, 'alerts.csv'))
            with open('data/mypings.json', 'r') as fp:
                await self.client.get_channel(841561036305465344).send(file=discord.File(fp, 'mypings.json'))
            await git_pull(ctx)
            p = subprocess.Popen(['restart'])
            sys.exit(0)
        else:
            await ctx.channel.send("NO")

    @commands.command(aliases=['contribute', 'support'])
    async def _support(self, ctx, *params):
        Embeds = discord.Embed(title="Contributions", color=0x00ff00)
        Embeds.add_field(
            name="Github repo", value="https://github.com/thesuhas/Covid19-India-Discord-Bot/", inline=False)
        Embeds.add_field(
            name='\u200b', value="If you wish to contribute to the bot, run these steps:", inline=False)
        rules = {
            1: "Fork this repository",
            2: "Create a new branch called `beta-username`",
            3: "Do whatever changes you wish to do and create a pull request with the following information furnished in the request message: `The functionality you wish to change/add | What did you change/add`",
            4: "Send a review request to any of the following members: `thesuhas`, `RIT3shSapata`, `sach-12`, `ArvindAROO` and/or `rohangrge`",
            5: "Wait for approval for reviewers. Your PR may be directly accepted or requested for further changes."
        }
        for ruleNo in rules:
            Embeds.add_field(name='\u200b', value="`" +
                            str(ruleNo) + '`: ' + rules[ruleNo], inline=False)

        guildObj = self.client.get_guild(742797665301168220)
        stark = guildObj.get_member(718845827413442692).mention
        sapota = guildObj.get_member(404597472103759872).mention
        suhas = guildObj.get_member(554876169363652620).mention
        sach = guildObj.get_member(723377619420184668).mention
        rohan = guildObj.get_member(771985293011058708).mention
        Embeds.add_field(name="Reviewers", value="`thesuhas` - {}\n`ArvindAROO` - {}\n`RIT3shSapata` - {}\n`sach-12` - {} and\n`rohangrge` - {}".format(
            suhas, stark, sapota, sach, rohan), inline=False)
        Embeds.add_field(
            name="Important", value="**Under no circumstances is anyone allowed to merge to the main branch.**", inline=False)
        Embeds.add_field(
            name="\u200b", value="You can send suggestions and feedback to covidindiabot@gmail.com")
        await ctx.send(embed=Embeds)

    @commands.command(aliases=['invite'])
    async def invite_command(self, ctx):
        await ctx.send("Invite me to your server with this link:\nhttps://bit.ly/covid-india-bot")

    @commands.command(aliases=['h', 'help'])
    async def help_command(self, ctx, text=''):
        if text == '':
            help_embed = discord.Embed(
                title="**Help**", color=discord.Color.green())
            help_embed.add_field(
                name='**`.india`**', value='Get COVID-19 stats of the entire nation', inline=False)
            help_embed.add_field(
                name='**`.states`**', value='Get a list of states', inline=False)
            help_embed.add_field(
                name='**`.state {state}`**', value='Get cases in that particular state', inline=False)
            help_embed.add_field(
                name='**`.vaccine {pincode} [date]`**', value='Get vaccination slots near you. If `date` is not mentioned, it will take today\'s date', inline=False)
            help_embed.add_field(
                name='**`.beds {type of hospital}`**', value='Get available beds. Type can be `government/govt` or `private`(Only Bengaluru)', inline=False)
            help_embed.add_field(
                name='**`.alerts {channel name}`**', value='(only for members with \"Manage Server\" permissions) To register any channel on your server to get important alerts from the developers', inline=False)
            help_embed.add_field(
                name='**`.removealerts`**', value='(only for members with \"Manage Server\" permissions) To de-register any channel that was registered for alerts', inline=False)
            help_embed.add_field(
                name='**`.invite`**', value='Get the invite link of the bot', inline=False)
            help_embed.add_field(
                name='**`.contribute`**', value='If you wish to contribute or learn about the bot', inline=False)
            help_embed.add_field(
                name='**`.reachout`**', value='(only for Server Administrators) To reach out to the bot developers', inline=False)
            await ctx.send(embed=help_embed)
        else:
            embed = discord.Embed(title='help', color=discord.Color.green(
            ), description='`.help` does not take any arguments.\n**Syntax:** `.help`')
            await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="help", description="Commands available from me")
    async def help_slash(self, ctx):
        await ctx.defer()
        help_embed = discord.Embed(title="**Help**", color=discord.Color.green())
        help_embed.add_field(
            name='**`.india`**', value='Get COVID-19 stats of the entire nation', inline=False)
        help_embed.add_field(name='**`.states`**',
                            value='Get a list of states', inline=False)
        help_embed.add_field(
            name='**`.state {state}`**', value='Get cases in that particular state', inline=False)
        help_embed.add_field(
            name='**`.vaccine {pincode} [date]`**', value='Get vaccination slots near you. If `date` is not mentioned, it will take today\'s date', inline=False)
        help_embed.add_field(name='**`.beds {type of hospital}`**',
                            value='Get available beds. Type can be `government/govt` or `private`(Only Bengaluru)', inline=False)
        help_embed.add_field(name='**`.alerts {channel name}`**',
                            value='(only for members with \"Manage Server\" permissions) To register any channel on your server to get important alerts from the developers', inline=False)
        help_embed.add_field(name='**`.removealerts`**',
                            value='(only for members with \"Manage Server\" permissions) To de-register any channel that was registered for alerts', inline=False)
        help_embed.add_field(name='**`.invite`**',
                            value='Get the invite link of the bot', inline=False)
        help_embed.add_field(name='**`.contribute`**',
                            value='If you wish to contribute or learn about the bot', inline=False)
        help_embed.add_field(name='**`.reachout`**',
                            value='(only for Server Administrators) To reach out to the bot developers', inline=False)
        await ctx.send(embeds=[help_embed])

    @commands.command(aliases=['removealerts'])
    async def removealerts_command(self, ctx, dest: discord.TextChannel = None):
        found = False
        if(dest == None):
            await ctx.send("Mention the channel you want to remove the alerts from")
            return
        auth_perms = ctx.channel.permissions_for(ctx.author)
        if(auth_perms.manage_guild):
            fp = open('data/alerts.csv', 'r')
            for line1 in fp:
                if(str(dest.id) in str(line1.split(',')[1].rstrip('\n'))):
                    fp.close()
                    found = True
                    break
                else:
                    continue
            if(not found):
                await ctx.send(f"Looks like {dest.mention} was never set up for alerts")
                fp.close()
                return
            dat = ''
            fp = open('data/alerts.csv', 'r')
            for line1 in fp:
                if(str(dest.id) not in str(line1.split(',')[1].rstrip('\n'))):
                    dat += line1
            fp.close()
            fp = open('data/alerts.csv', 'w')
            fp.write(dat)
            fp.close()
            await ctx.send(f"**DONE**. {dest.mention} will no longer receive alerts and updates from the developers")
            Cowin.updatecsvdata(Cowin)
        else:
            await ctx.send("Looks like you don't have the manage server permissions to run this")


    @commands.command(aliases=['reachout'])
    async def reachout_command(self, ctx, *, msg: str = ''):
        if(msg == ''):
            await ctx.send("Type a message to send to the developers")
            return
        auth_perms = ctx.channel.permissions_for(ctx.author)
        if(auth_perms.administrator):
            await ctx.send("Your message has been sent to the devs. We will get back to you with a reply shortly on this channel")
            await self.client.get_channel(841560857602162698).send(f"Reachout from `{ctx.guild.name}`, guild-ID: `{ctx.guild.id}`, channel-ID: `{ctx.channel.id}`\n\n{msg}")
        else:
            await ctx.send("Only members with administrator perms can run this command. Contact your server admin or anyone with a role who has administrator privileges. You can always contact us on `covidindiabot@gmail.com`")

    @commands.command(aliases=['alerts'])
    async def alerts_command(self, ctx, dest: discord.TextChannel = None):
        if(dest == None):
            await ctx.send("Mention the channel you want to send alerts to")
            return
        auth_perms = ctx.channel.permissions_for(ctx.author)
        if(auth_perms.manage_guild):
            file1 = open('data/alerts.csv', 'r')
            for line in file1:
                if(str(dest.id) in str(line.split(',')[1].rstrip('\n'))):
                    await ctx.send(f"Looks like {dest.mention} is already subscribed to our alerts")
                    file1.close()
                    return
            client_member = ctx.guild.get_member(836578128305717279)
            client_perms = client_member.permissions_in(dest)
            if(client_perms.send_messages and client_perms.embed_links and client_perms.attach_files):
                file1 = open('data/alerts.csv', 'a')
                file1.write(f"{ctx.guild.id},{dest.id}\n")
                file1.close()
                await ctx.send(f"**Success!** You'll now get vaccine slot alerts in Bengaluru and other important notifications from the bot on {dest.mention}")
                Cowin.updatecsvdata(Cowin)
            else:
                await ctx.send("I don't have enough permissions in that channel. Enable `Send Messages`, `Embed Links` and `Attach Files` for me")
        else:
            await ctx.send("Looks like you don't have the manage server permissions to run this")

    @commands.command(aliases=['myping', 'mp'])
    async def personalpingcommand(self, ctx, pincode: int = 0):
        await ctx.channel.trigger_typing()
        found = False
        pincheck = Helpers.pincodecheckbangalore(str(pincode))
        if pincheck:
            with open('data/alerts.csv', 'r') as fp:
                for line in fp:
                    if(str(ctx.guild.id) in line.split(',')[0]):
                        found = True
            if not found:
                await ctx.send("Looks like your server isn't set up for vaccine alerts at all.\nContact your server moderators and ask them to run the `.alerts` command and then try again")
                fp.close()
                return
            fp = open('data/mypings.json', 'r')
            data = json.load(fp)
            fp.close()
            user_id = str(ctx.author.id)
            guild_id = str(ctx.guild.id)
            subdict = {}
            if(str(pincode) in data):
                subdict = data[str(pincode)]
                if(user_id in subdict):
                    await ctx.send("Looks like you've already subscribed for this pincode")
                    return
            subdict[user_id] = guild_id
            data[str(pincode)] = subdict
            fp = open('data/mypings.json', 'w')
            json.dump(data, fp)
            fp.close()
            Cowin.updatejsondata(Cowin)
            await ctx.send(f"You'll now get a ping every time there's a slot open in pincode: **{pincode}**")
        else:
            await ctx.send("Pincode invalid, try again")

    @commands.command(aliases=['rp', 'removeping'])
    async def removepingcommand(self, ctx, pincode: int = 0):
        await ctx.channel.trigger_typing()
        pincheck = Helpers.pincodecheckbangalore(str(pincode))
        if pincheck:
            fp = open('data/mypings.json', 'r')
            data = json.load(fp)
            fp.close()
            user_id = str(ctx.author.id)
            try:
                subdict = data[str(pincode)]
                subdict.pop(user_id)
            except KeyError:
                await ctx.send(f"No record of pincode: **{pincode}** was found in our database")
                return
            data[str(pincode)] = subdict
            fp = open('data/mypings.json', 'w')
            json.dump(data, fp)
            fp.close()
            Cowin.updatejsondata(Cowin)
            await ctx.send(f"Alright, no more pings for pincode: **{pincode}**")
        else:
            await ctx.send("Pincode invalid, try again")

    @commands.command(aliases=['lp', 'listpings'])
    async def pinglist(self, ctx):
        fp = open('data/mypings.json', 'r')
        data = json.load(fp)
        fp.close()
        user_id = str(ctx.author.id)
        pinlist = ''
        for pincodes in data:
            id_dict = data[pincodes]
            for uid in id_dict:
                if user_id in str(uid):
                    pinlist += f"{pincodes}\n"
        if pinlist == '':
            await ctx.send("You haven't set up for any pincode pings. To do so, use `.myping`")
        else:
            await ctx.send(f"You've set up to get pings for the following pincodes:\n{pinlist}")





def setup(client):
    client.add_cog(Misc(client))
