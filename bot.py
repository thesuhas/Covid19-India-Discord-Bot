from typing_extensions import TypeAlias
import requests
import pandas as pd
import io
import discord
import datetime
from babel.numbers import format_currency
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from discord_slash import SlashCommand
import datetime
import dataframe_image as dfi
import math
import csv
import re

# Create a bot instance and sets a command prefix
client = commands.Bot(command_prefix='.', intents=discord.Intents.all())
client.remove_command('help')

# load the env variable token
load_dotenv()

# Saving file name
filename = 'states.csv'
file_daily = "states_yesterday.csv"

# Mapping for queries to states_yesterday
mapp = {"total": 'TT', 'andaman and nicobar islands': 'AN', "andhra pradesh": 'AP', "arunachal pradesh": 'AR', "assam": 'AS', "bihar": 'BR', "chandigarh": 'CH', "chhattisgarh": 'CT', "dadra and nagar haveli and daman and diu": 'DN', "dadra and nagar haveli and daman and diu": 'DD', "delhi": 'DL', "goa": 'GA', "gujarat": 'GJ', "haryana": 'HR', "himachal pradesh": 'HP', "jammu and kashmir": 'JK', "jharkhand": 'JH',
        "karnataka": 'KA', "kerala": 'KL', "ladakh": 'LA', "lakshadweep": 'LD', "madhya pradesh": 'MP', "maharashtra": 'MH', "manipur": 'MN', "meghalaya": 'ML', "mizoram": 'MZ', "nagaland": 'NL', "odisha": 'OR', "puducherry": 'PY', "punjab": 'PB', "rajasthan": 'RJ', "sikkim": 'SK', "tamil nadu": 'TN', "telangana": 'TG', "tripura": 'TR', "uttar pradesh": 'UP', "uttarakhand": 'UT', "west bengal": 'WB', "state unassigned": 'UN'}
CHANNELLIST = []
PINGLIST = []

def updateFileValues():
    with open('alerts.csv', 'r') as f:
        for line in f.readlines():
            lineLst = line.split(',')
            CHANNELLIST.append([int(lineLst[0]), int(lineLst[1])])
        f.close()

    with open('mypings.csv', 'r') as f:
        for line in f.readlines():
            lineLst = line.split(',')
            PINGLIST.append([int(lineLst[0]), int(lineLst[1]),int(lineLst[2])])
        f.close()

# Initialising df to something
df = 0
df_daily = 0

# Update variable
footer = 0

# Initialising states list
s = list()

# Initialising slash command
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    updateFileValues()
    global df
    global df_daily
    global s
    global footer
    # Start updation loop
    update.start()
    update_daily.start()
    alert.start()
    # Create basic data frame and store
    test = requests.get(
        'https://api.covid19india.org/csv/latest/state_wise.csv')
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
    print("df Updated at: ", datetime.datetime.now())
    time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
    time = time.strftime("%d-%b") + ' at ' + time.strftime("%I:%M %p")
    footer = f"Last Updated: {time}"

    # Creating daily df
    response = requests.get(
        'https://api.covid19india.org/csv/latest/state_wise_daily.csv')
    response = str(response.text)
    data_daily = io.StringIO(response)
    df1 = pd.read_csv(data_daily, sep=",")
    # Get yestedays date in appropriate formatting
    t = datetime.datetime.now() - datetime.timedelta(days=1)
    t = t.strftime("%d-%b-%y")
    df_daily = df1[df1['Date'] == t]
    if len(df_daily) > 0:
        df_daily.to_csv(file_daily)
        print("df_daily Updated at: ", datetime.datetime.now())

    activity = discord.Activity(
        name="Plague Inc.", type=discord.ActivityType.playing)
    await client.change_presence(activity=activity)
    await client.get_channel(841561036305465344).send(f"Bot is online")


@client.event
async def on_guild_join(guild):
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


@client.event
async def on_guild_remove(guild):
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
    updateFileValues()



@client.event
async def on_message(message):
    if message.author.bot:
        if((message.channel.id == 840644400564142111) and (message.author.id == 836578128305717279)):
            await message.publish()
        else:
            pass
    elif (('<@!836578128305717279>' in message.content) or ('<@836578128305717279>' in message.content)):
        await message.channel.send(f"{message.author.mention} my prefix in this server is `.`\nUse `.help` to know what all I can do")
    else:
        await client.process_commands(message)


@client.event
async def on_member_remove(member):
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


@client.command(aliases=['file', 'f'])
async def file_command(ctx):
    if((ctx.author.id == 554876169363652620) or (ctx.author.id == 723377619420184668) or (ctx.author.id == 718845827413442692) or (ctx.author.id == 404597472103759872) or (ctx.author.id == 771985293011058708)):
        await ctx.send("You have clearance")
        with open('alerts.csv', 'r') as fp:
            await client.get_channel(841561036305465344).send(file=discord.File(fp, 'alerts.csv'))
        fp.close()
        with open('mypings.csv', 'r') as fp:
            await client.get_channel(841561036305465344).send(file=discord.File(fp, 'mypings.csv'))
        fp.close()
    else:
        await ctx.send("You are not authorised to run this command")


@client.command(aliases=['guilds'])
async def guilds_command(ctx):
    if((ctx.author.id == 554876169363652620) or (ctx.author.id == 723377619420184668) or (ctx.author.id == 718845827413442692) or (ctx.author.id == 404597472103759872) or (ctx.author.id == 771985293011058708)):
        await ctx.channel.trigger_typing()
        count = 0
        dat = 'SERVER NAME,SERVER ID\n\n'
        guilds_details = await client.fetch_guilds(limit=150).flatten()
        for guild_deets in guilds_details:
            dat += f"{guild_deets.name},{guild_deets.id}\n"
            count += 1
        dat += f"\nCOUNT: {count}"
        with open('guilds.csv', 'w+') as fp:
            fp.write(dat)
        await ctx.send("You have clearance")
        await client.get_channel(841561036305465344).send(file=discord.File('guilds.csv'))
        fp.close()
        os.remove('guilds.csv')
    else:
        await ctx.send("You are not authorised for this")


@client.command(aliases=['contribute', 'support'])
async def _support(ctx, *params):
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

    guildObj = client.get_guild(742797665301168220)
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


@client.command(aliases=['invite'])
async def invite_command(ctx):
    await ctx.send("Invite me to your server with this link:\nhttps://bit.ly/covid-india-bot")


@client.command(aliases=['h', 'help'])
async def help_command(ctx, text=''):
    if text == '':
        help_embed = discord.Embed(
            title="**Help**", color=discord.Color.green())
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
        help_embed.add_field(
            name='**`.alerts {channel name}`**', value='(only for members with \"Manage Server\" permissions) To register any channel on your server to get important alerts from the developers', inline=False)
        help_embed.add_field(name='**`.removealerts`**',
                             value='(only for members with \"Manage Server\" permissions) To de-register any channel that was registered for alerts', inline=False)
        help_embed.add_field(
            name='**`.invite`**', value='Get the invite link of the bot', inline=False)
        help_embed.add_field(name='**`.contribute`**',
                             value='If you wish to contribute or learn about the bot', inline=False)
        help_embed.add_field(
            name='**`.reachout`**', value='(only for Server Administrators) To reach out to the bot developers', inline=False)
        await ctx.send(embed=help_embed)
    else:
        embed = discord.Embed(title='help', color=discord.Color.green(
        ), description='`.help` does not take any arguments.\n**Syntax:** `.help`')
        await ctx.send(embed=embed)

# Slash Command of the same


@slash.slash(name="help", description="Commands available from me")
async def help_slash(ctx):
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


@client.command(aliases=['state'])
async def state_command(ctx, *, state=''):
    state = state.lower()
    if state == '':
        # If state has not been mentioned
        embed = discord.Embed(title="State", color=discord.Color.green(
        ), description='Need to mention a state.\n**Syntax:** `.state {state}`\n Run `.help` for more info')
        await ctx.send(embed=embed)
    else:
        if (state.lower() == "total"):
            await ctx.send("Use `.india` for total cases")
        else:
            entry = df.loc[df['State'] == state.lower()]
            if entry.empty:
                await ctx.send("Chosen state not available")
            else:
                #m = f"**Covid Cases in {state[0].upper() + state[1:]}:**\nConfirmed: {entry['Confirmed'].values[0]}\nRecovered: {entry['Recovered'].values[0]}\nDeaths: {entry['Deaths'].values[0]}\nActive: {entry['Active'].values[0]}"
                embed = discord.Embed(
                    title=f"Cases in {state[0].upper() + state[1:]}", color=discord.Color.green())
                embed.add_field(name='Active', value=format_currency(
                    int(entry['Active'].values[0]), 'INR', locale='en_IN')[1:-3], inline=False)
                embed.add_field(name='Confirmed', value=format_currency(int(entry['Confirmed'].values[0]), 'INR', locale='en_IN')[
                                1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Confirmed'][mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                embed.add_field(name='Recovered', value=format_currency(int(entry['Recovered'].values[0]), 'INR', locale='en_IN')[
                                1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Recovered'][mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                embed.add_field(name='Deaths', value=format_currency(int(entry['Deaths'].values[0]), 'INR', locale='en_IN')[
                                1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Deceased'][mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                embed.set_footer(text=footer)
                await ctx.send(embed=embed)

# Slash command of state


@slash.slash(name='state', description='State-wise stats of COVID-19')
async def state_slash(ctx, *, state=''):
    # .defer lets bot think for upto 15 seconds
    await ctx.defer()
    if state == '':
        # If state has not been mentioned
        embed = discord.Embed(title="State", color=discord.Color.green(
        ), description='Need to mention a state.\n**Syntax:** `.state {state}`\n Run `.help` for more info')
        await ctx.send(embed=embed)
    else:
        if (state.lower() == "total"):
            await ctx.send("Use `.india` for total cases")
        else:
            entry = df.loc[df['State'] == state.lower()]
            if entry.empty:
                await ctx.send("Chosen state not available")
            else:
                #m = f"**Covid Cases in {state[0].upper() + state[1:]}:**\nConfirmed: {entry['Confirmed'].values[0]}\nRecovered: {entry['Recovered'].values[0]}\nDeaths: {entry['Deaths'].values[0]}\nActive: {entry['Active'].values[0]}"
                embed = discord.Embed(
                    title=f"Cases in {state[0].upper() + state[1:]}", color=discord.Color.green())
                embed.add_field(name='Active', value=format_currency(
                    int(entry['Active'].values[0]), 'INR', locale='en_IN')[1:-3], inline=False)
                embed.add_field(name='Confirmed', value=format_currency(int(entry['Confirmed'].values[0]), 'INR', locale='en_IN')[
                                1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Confirmed'][mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                embed.add_field(name='Recovered', value=format_currency(int(entry['Recovered'].values[0]), 'INR', locale='en_IN')[
                                1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Recovered'][mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                embed.add_field(name='Deaths', value=format_currency(int(entry['Deaths'].values[0]), 'INR', locale='en_IN')[
                                1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Deceased'][mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                embed.set_footer(text=footer)
                await ctx.send(embed=embed)


@client.command(aliases=['india'])
async def india_command(ctx):
    entry = df.loc[df['State'] == 'total']
    #m = f"**Covid Cases in the country:**\nConfirmed: {entry['Confirmed'].values[0]}\nRecovered: {entry['Recovered'].values[0]}\nDeaths: {entry['Deaths'].values[0]}\nActive: {entry['Active'].values[0]}"
    embed = discord.Embed(title="Cases in the Country",
                          color=discord.Color.green())
    embed.add_field(name='Active', value=format_currency(
        int(entry['Active'].values[0]), 'INR', locale='en_IN')[1:-3], inline=False)
    embed.add_field(name='Confirmed', value=format_currency(int(entry['Confirmed'].values[0]), 'INR', locale='en_IN')[
                    1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Confirmed'][mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
    embed.add_field(name='Recovered', value=format_currency(int(entry['Recovered'].values[0]), 'INR', locale='en_IN')[
                    1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Recovered'][mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
    embed.add_field(name='Deaths', value=format_currency(int(entry['Deaths'].values[0]), 'INR', locale='en_IN')[
                    1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Deceased'][mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
    embed.set_footer(text=footer)
    await ctx.send(embed=embed)

# Slash command of the above


@slash.slash(name='india', description='Stats of COVID-19 in India')
async def india_slash(ctx):
    await ctx.defer()
    entry = df.loc[df['State'] == 'total']
    embed = discord.Embed(title="Cases in the Country",
                          color=discord.Color.green())
    embed.add_field(name='Active', value=format_currency(
        int(entry['Active'].values[0]), 'INR', locale='en_IN')[1:-3], inline=False)
    embed.add_field(name='Confirmed', value=format_currency(int(entry['Confirmed'].values[0]), 'INR', locale='en_IN')[
                    1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Confirmed'][mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
    embed.add_field(name='Recovered', value=format_currency(int(entry['Recovered'].values[0]), 'INR', locale='en_IN')[
                    1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Recovered'][mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
    embed.add_field(name='Deaths', value=format_currency(int(entry['Deaths'].values[0]), 'INR', locale='en_IN')[
                    1:-3] + '\n(+' + format_currency(int(df_daily[df_daily['Status'] == 'Deceased'][mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
    embed.set_footer(text=footer)
    await ctx.send(embeds=[embed])


@client.command(aliases=['states'])
async def states_command(ctx, text=''):
    global s
    if text != '':
        await ctx.send('Wrong usage of command, check `.help`')
    else:
        # Returns list of states
        string = '**States and Union Territories:\n**'
        for i in s:
            string += i + '\n'
        await ctx.send(string)


@client.command(aliases=['vaccine'])
async def vaccine_command(ctx, pincode="", date=datetime.datetime.now().strftime("%d-%m-%Y")):
    # If no pincode given
    if pincode == "":
        await ctx.send("No pincode mentioned")
    else:
        headers = {"Accept-Language": "en-IN",
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        data = {"pincode": pincode, "date": date}
        res = requests.get(
            "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin", headers=headers, params=data)
        if res.status_code == 400:
            await ctx.send("Invalid pincode")
            return
        if res.status_code == 403:
            await ctx.send("API is unresponsive at the time. Please try again after sometime")
            return
        # Extracting json data
        data = res.json()
        sessions = dict()
        if len(data['centers']) > 0:
            for i in data['centers']:
                # Look at all sessions
                for j in i['sessions']:
                    # If there is an available session
                    if j['available_capacity'] >= 1:
                        # Check if hospital exists
                        if (i['name'], i['pincode'], i['fee_type'], i['address']) in sessions:
                            sessions[(i['name'], i['pincode'], i['fee_type'], i['address'])].append(j)
                        else:
                            sessions[(i['name'], i['pincode'], i['fee_type'], i['address'])] = list()
                            sessions[(i['name'], i['pincode'], i['fee_type'], i['address'])].append(j)
            if len(sessions) == 0:
                await ctx.send("No available sessions")
            else:
                # Create an embed for every session
                for sesh in sessions:
                    embed = discord.Embed(
                        title=f"Vaccine Available at {sesh[0]}", color=discord.Color.green())
                    embed.add_field(name='Date', value=date, inline=False)
                    embed.add_field(
                            name='Address', value=sesh[3], inline=False)
                    embed.add_field(
                            name='Pin Code', value=sesh[1], inline=False)
                    embed.add_field(
                        name='Available Capacity for Dose 1', value=sessions[sesh][0]['available_capacity_dose1'], inline=False)
                    embed.add_field(
                        name='Available Capacity for Dose 2', value=sessions[sesh][0]['available_capacity_dose2'], inline=False)
                    embed.add_field(
                        name='Minimum Age', value=sessions[sesh][0]['min_age_limit'], inline=False)
                    embed.add_field(
                        name='Vaccine', value=sessions[sesh][0]['vaccine'])
                    embed.add_field(
                            name='Fee type', value=sesh[2], inline=False)
                    embed.add_field(name="Slots", value='\n'.join(
                        sessions[sesh][0]['slots']), inline=False)
                    await ctx.send(embed=embed)
        else:
            await ctx.send("No available vaccination center")


@slash.slash(name='vaccine', description='List of Vaccination slots near you')
async def vaccine_slash(ctx, pincode="", date=datetime.datetime.now().strftime("%d-%m-%Y")):
    await ctx.defer()
    # If no pincode given
    pincheck = await pincodecheckindia(pincode)
    if not pincheck:
        await ctx.send("Invalid pincode, try again")
    else:
        headers = {"Accept-Language": "en-IN",
                   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        data = {"pincode": pincode, "date": date}
        res = requests.get(
            "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin", headers=headers, params=data)
        # if res.status_code == 400:
        #     await ctx.send("Invalid pincode")
        #     return
        if res.status_code == 403:
            await ctx.send("API is unresponsive at the time. Please try again after sometime")
            return
        # Extracting json data
        data = res.json()
        sessions = dict()
        if len(data['centers']) > 0:
            #pprint.pprint(data)
            for i in data['centers']:

                # Look at all sessions
                for j in i['sessions']:
                    # If there is an available session
                    if j['available_capacity'] >= 1:
                        # Check if hospital exists
                        if i['name'] in sessions:
                            sessions[(i['name'], i['pincode'], i['fee_type'], i['address'])].append(j)
                        else:
                            sessions[(i['name'], i['pincode'], i['fee_type'], i['address'])] = list()
                            sessions[(i['name'], i['pincode'], i['fee_type'], i['address'])].append(j)
            if len(sessions) == 0:
                await ctx.send("No available sessions")
            else:
                # Create an embed for every session
                for sesh in sessions:
                    embed = discord.Embed(
                        title=f"Vaccine Available at {sesh[0]}", color=discord.Color.green())
                    embed.add_field(name='Date', value=date, inline=False)
                    embed.add_field(
                            name='Address', value=sesh[3], inline=False)
                    embed.add_field(
                            name='Pin Code', value=sesh[1], inline=False)
                    embed.add_field(
                        name='Available Capacity for Dose 1', value=sessions[sesh][0]['available_capacity_dose1'], inline=False)
                    embed.add_field(
                        name='Available Capacity for Dose 2', value=sessions[sesh][0]['available_capacity_dose2'], inline=False)
                    embed.add_field(
                        name='Minimum Age', value=sessions[sesh][0]['min_age_limit'], inline=False)
                    embed.add_field(
                        name='Vaccine', value=sessions[sesh][0]['vaccine'])
                    embed.add_field(
                            name='Fee type', value=sesh[2], inline=False)
                    embed.add_field(name="Slots", value='\n'.join(
                        sessions[sesh][0]['slots']), inline=False)
                    await ctx.send(embed=embed)
        else:
            await ctx.send("No available vaccination center")


@tasks.loop(seconds=1800)
async def update_daily():
    global df_daily
    # Creating daily df
    response = requests.get(
        'https://api.covid19india.org/csv/latest/state_wise_daily.csv')
    response = str(response.text)
    data_daily = io.StringIO(response)
    df1 = pd.read_csv(data_daily, sep=",")
    # Get yestedays date in appropriate formatting
    t = datetime.datetime.now() - datetime.timedelta(days=1)
    t = t.strftime("%d-%b-%y")
    df_daily = df1[df1['Date'] == t]
    if len(df_daily) > 0:
        df_daily.to_csv(file_daily)
        print("df_daily Updated at: ", datetime.datetime.now())


@client.command(aliases=['beds'])
async def beds_command(ctx, hospital=''):
    hospital = hospital.lower()
    if hospital == '':
        await ctx.send("Mention type of hospital. Example: `.beds government`")
    elif hospital != 'govt' and hospital != 'government' and hospital != 'private':
        await ctx.send("Hospital types are: `government/govt` and `private`")
    else:
        if hospital == 'govt':
            hospital = "government"
        df = pd.read_html("https://bbmpgov.com/chbms/#A")
        keys = {"government": 2, "private": 4}
        df = df[keys[hospital]].sort_values(by=[('Net Available Beds for C+ Patients',            'Total')],
                                            ascending=False).reset_index(drop=True).drop([('SR. NO.',                '#')], axis=1)[:10]
        df = df[[('Dedicated Covid Healthcare Centers (DCHCs)', 'Name of facility'),
                 ('Net Available Beds for C+ Patients',              'Gen'),
                 ('Net Available Beds for C+ Patients',              'HDU'),
                 ('Net Available Beds for C+ Patients',              'ICU'),
                 ('Net Available Beds for C+ Patients',         'ICUVentl'),
                 ('Net Available Beds for C+ Patients',            'Total')]]
        df.columns = ['Hospital', 'Gen', 'HDU', 'ICU', 'ICUVentl', 'Total']
        dfi.export(df, 'test.png', table_conversion='matplotlib')

        await ctx.send(file=discord.File('test.png'))


@slash.slash(name='beds', description='Hospitals with beds')
async def beds_slash(ctx, hospital_type):
    hospital = hospital_type
    hospital = hospital.lower()
    if hospital == '':
        await ctx.send("Mention type of hospital. Example: `.beds government`")
    elif hospital != 'govt' and hospital != 'government' and hospital != 'private':
        await ctx.send("Hospital types are: `government/govt` and `private`")
    else:
        if hospital == 'govt':
            hospital = "government"
        df = pd.read_html("https://bbmpgov.com/chbms/#A")
        keys = {"government": 2, "private": 4}
        df = df[keys[hospital]].sort_values(by=[('Net Available Beds for C+ Patients',            'Total')],
                                            ascending=False).reset_index(drop=True).drop([('SR. NO.',                '#')], axis=1)[:10]
        df = df[[('Dedicated Covid Healthcare Centers (DCHCs)', 'Name of facility'),
                 ('Net Available Beds for C+ Patients',              'Gen'),
                 ('Net Available Beds for C+ Patients',              'HDU'),
                 ('Net Available Beds for C+ Patients',              'ICU'),
                 ('Net Available Beds for C+ Patients',         'ICUVentl'),
                 ('Net Available Beds for C+ Patients',            'Total')]]
        df.columns = ['Hospital', 'Gen', 'HDU', 'ICU', 'ICUVentl', 'Total']
        dfi.export(df, 'test.png', table_conversion='matplotlib')

        await ctx.send(file=discord.File('test.png'))

# Updates dataframe every 30 mins


@tasks.loop(seconds=1800)
async def update():
    global footer
    global df
    # Create basic data frame and store
    test = requests.get(
        'https://api.covid19india.org/csv/latest/state_wise.csv')
    test = str(test.text)

    data = io.StringIO(test)
    df = pd.read_csv(data, sep=",")
    # Making states lowercase
    df["State"] = df["State"].str.lower()
    df.to_csv(filename)
    # Prints when df is last updated
    print("df Updated at: ", datetime.datetime.now())
    time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
    time = time.strftime("%d-%b") + ' at ' + time.strftime("%I:%M %p")
    footer = f"Last Updated: {time}"


@tasks.loop(seconds=20)
async def alert():
    date = datetime.datetime.now().strftime("%d-%m-%Y")
    datetom = (datetime.datetime.now() +
               datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    dates = [date, datetom]
    d_ids = [276, 265, 294]
    for j in d_ids:
        if(j == 276):
            url = os.getenv("url1")
        if(j == 265):
            url = os.getenv("url2")
        if(j == 294):
            url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"
        for i in dates:
            headers = {"Accept-Language": "en-IN",
                       'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            data = {"district_id": j, "date": i}
            if(j == 294):
                res = requests.get(url, headers=headers, params=data)
            else:
                res = requests.get(url, params=data)
            #resp = res.json()
            #print(res.json())
            #print(res.status_code, j)
            if(res.status_code == 200):
                resp = res.json()
                for k in resp['sessions']:
                    if(len(k) != 0):
                        if(math.trunc(k['available_capacity_dose1']) >= 8 and k['min_age_limit'] == 18 and ((k['available_capacity_dose1'])-int(k['available_capacity_dose1'])) == 0):
                            embed = discord.Embed(
                                title=f"Vaccine Available at {k['name']}", color=discord.Color.green())
                            embed.add_field(
                                name='Date', value=k['date'], inline=False)
                            embed.add_field(
                                name='Address', value=k['address'], inline=False)
                            embed.add_field(
                                name='Pincode', value=k['pincode'], inline=False)
                            embed.add_field(
                                name='Available Capacity for Dose 1', value=k['available_capacity_dose1'], inline=False)
                            embed.add_field(
                                name='Available Capacity for Dose 2', value=k['available_capacity_dose2'], inline=False)
                            embed.add_field(
                                name='Minimum Age', value=k['min_age_limit'], inline=False)
                            embed.add_field(
                                name='Vaccine', value=k['vaccine'])
                            embed.add_field(
                                name='Fee type', value=k['fee_type'], inline=False)
                            embed.add_field(name="Slots", value='\n'.join(
                                k['slots']), inline=False)

                            ch_list = [i[1] for i in CHANNELLIST] 
                            for ch in ch_list:
                                await client.get_channel(int(ch)).send(embed=embed)
                                try:
                                    for line in PINGLIST:
                                        p_codes = line[2]
                                        file_guild_ids = line[1]
                                        channel_guild_id = client.get_channel(int(ch)).guild.id
                                        if((str(k['pincode']) in p_codes) and (str(channel_guild_id) in file_guild_ids)):
                                            member_id = int(line.split(',')[0])
                                            memberObj = client.get_user(member_id)
                                            await client.get_channel(int(ch)).send(memberObj.mention)
                                except Exception as e:
                                    continue
                            #await client.get_channel(841561036305465344).send(embed=embed)
                            # fp.close()
                            # fp2.close()
                                

                    else:
                        continue
            else:
                continue


@client.command(aliases=['alerts'])
async def alerts_command(ctx, dest: discord.TextChannel = None):
    if(dest == None):
        await ctx.send("Mention the channel you want to send alerts to")
        return
    auth_perms = ctx.channel.permissions_for(ctx.author)
    if(auth_perms.manage_guild):
        file1 = open('alerts.csv', 'r')
        for line in file1:
            if(str(dest.id) in str(line.split(',')[1].rstrip('\n'))):
                await ctx.send(f"Looks like {dest.mention} is already subscribed to our alerts")
                file1.close()
                return
        client_member = ctx.guild.get_member(836578128305717279)
        client_perms = client_member.permissions_in(dest)
        if(client_perms.send_messages and client_perms.embed_links):
            file1 = open('alerts.csv', 'a')
            file1.write(f"{ctx.guild.id},{dest.id}\n")
            file1.close()
            await ctx.send(f"**Success!** You'll now get vaccine slot alerts in Bengaluru and other important notifications from the bot on {dest.mention}")
            updateFileValues()
        else:
            await ctx.send("I don't have enough permissions in that channel. Enable `Send Messages` and `Embed Links` for me")
    else:
        await ctx.send("Looks like you don't have the manage server permissions to run this")


@client.command(aliases=['removealerts'])
async def removealerts_command(ctx, dest: discord.TextChannel = None):
    found = False
    if(dest == None):
        await ctx.send("Mention the channel you want to remove the alerts from")
        return
    auth_perms = ctx.channel.permissions_for(ctx.author)
    if(auth_perms.manage_guild):
        fp = open('alerts.csv', 'r')
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
        fp = open('alerts.csv', 'r')
        for line1 in fp:
            if(str(dest.id) not in str(line1.split(',')[1].rstrip('\n'))):
                dat += line1
        fp.close()
        fp = open('alerts.csv', 'w')
        fp.write(dat)
        fp.close()
        await ctx.send(f"**DONE**. {dest.mention} will no longer receive alerts and updates from the developers")
        updateFileValues()
    else:
        await ctx.send("Looks like you don't have the manage server permissions to run this")


@client.command(aliases=['announce'])
async def announce_command(ctx, *, msg: str = ''):
    if((ctx.author.id == 554876169363652620) or (ctx.author.id == 723377619420184668) or (ctx.author.id == 718845827413442692) or (ctx.author.id == 404597472103759872) or (ctx.author.id == 771985293011058708)):
        if(msg == ''):
            await ctx.send("Put a message man")
            return
        ch_list = [i[1] for i in CHANNELLIST]
        for ch in ch_list:
            await client.get_channel(int(ch)).send(f"**NEW ALERT FROM THE DEVS**\n\n{msg}")
        await ctx.send("Announcement sent")

    else:
        await ctx.send("You don't have permission to execute this command")


@client.command(aliases=['reachout'])
async def reachout_command(ctx, *, msg: str = ''):
    if(msg == ''):
        await ctx.send("Type a message to send to the developers")
        return
    auth_perms = ctx.channel.permissions_for(ctx.author)
    if(auth_perms.administrator):
        await ctx.send("Your message has been sent to the devs. We will get back to you with a reply shortly on this channel")
        await client.get_channel(841560857602162698).send(f"Reachout from `{ctx.guild.name}`, guild-ID: `{ctx.guild.id}`, channel-ID: `{ctx.channel.id}`\n\n{msg}")
    else:
        await ctx.send("Only members with administrator perms can run this command. Contact your server admin or anyone with a role who has administrator privileges. You can always contact us on `covidindiabot@gmail.com`")


@client.command(aliases=['reachreply'])
async def reachreply_command(ctx, destid: int = 0, *, msg: str = ''):
    if((ctx.author.id == 554876169363652620) or (ctx.author.id == 723377619420184668) or (ctx.author.id == 718845827413442692) or (ctx.author.id == 404597472103759872) or (ctx.author.id == 771985293011058708)):
        if(destid == 0):
            await ctx.send("Saar, enter channel ID")
            return
        if(msg == ''):
            await ctx.send("Saar, tell something to reply to them")
            return
        try:
            dest = client.get_channel(destid)
        except:
            await ctx.send("Can't fetch that channel")
            return
        await dest.send("**MESSAGE FROM THE DEVS**")
        await dest.send(msg)
        await ctx.send("Message sent")
    else:
        await ctx.send("You do not have the permission to execute this command")


@client.command(aliases=['myping', 'mp'])
async def personalpingcommand(ctx, pincode:int = 0):
    found = False
    # if pincode == 0:
    #     await ctx.send("Enter a pincode")
    #     return
    # if(len(str(pincode)) != 6):
    #     await ctx.send("Enter a valid pincode")
    #     return
    pincheck = await pincodecheckbangalore(str(pincode))
    if pincheck:
        with open('alerts.csv', 'r') as fp:
            for line in fp:  
                if(str(ctx.guild.id) in line.replace('\n', '').split(',')[0]):
                    found = True
        if not found:
            await ctx.send("Looks like your server isn't set up for vaccine alerts at all.\nContact your server moderators and ask them to run the `.alerts` command and then try again")
            return
        fp.close()
        fp = open('mypings.csv', 'r')
        for line in fp:
            if((str(ctx.author.id) in line.replace('\n', '').split(',')[0]) and (str(pincode) in line.replace('\n', '').split(',')[2])):
                await ctx.send("Looks like you've already subscribed for this pincode")
                fp.close()
                return
        fp.close()
        fp = open('mypings.csv', 'a+')
        fp.write(f"{ctx.author.id},{ctx.guild.id},{pincode}\n")
        fp.close()
        await ctx.send(f"You'll now get a ping every time there's a slot open in pincode: **{pincode}**")
        updateFileValues()
    else:
        await ctx.send("Pincode invalid,try again")



@client.command(aliases=['rp', 'removeping'])
async def removepingcommand(ctx, pincode:int = 0):
    removed = False
    # if pincode == 0:
    #     await ctx.send("Enter a pincode")
    #     return
    # if(len(str(pincode)) != 6):
    #     await ctx.send("Enter a valid pincode")
        #return
    pincheck = await pincodecheckbangalore(str(pincode))
    if pincheck:
        dat =''
        fp = open('mypings.csv', 'r')
        for line in fp:
            if((str(ctx.author.id) in line.replace('\n', '').split(',')[0]) and (str(ctx.guild.id) in line.replace('\n', '').split(',')[1]) and (str(pincode) in line.replace('\n', '').split(',')[2])):
                removed = True
                continue
            dat += line
        fp.close()
        fp = open('mypings.csv', 'w')
        fp.write(dat)
        fp.close()
        if(removed):
            await ctx.send(f"Alright, no more pings for pincode: **{pincode}**")
        else:
            await ctx.send(f"No record of pincode: **{pincode}** was found in our database")
    else:
        await ctx.send("Pincode invalid,try again")

@client.command(aliases=['listpings', 'lp'])
async def pinglist(ctx):
    fp = open('mypings.csv', 'r')
    dat = ''
    for line in fp:
        if(str(ctx.author.id) == line.replace('\n', '').split(',')[0]):
            dat += line.replace('\n', '').split(',')[2] + "\n"
    fp.close()
    if dat == '':
        await ctx.send("You haven't set up for any personal pings. To do so, use `.personalping`")
    else:
        await ctx.send(f"You've set up to get pings for the following pincodes:\n{dat}")

async def pincodecheckindia(pincode):
    regex = "^[1-9]{1}[0-9]{2}\\s{0,1}[0-9]{3}$"
    pin = re.compile(regex)
    check = re.match(pin,pincode)
    if check is not None:
        return True
    else:
        return False

async def pincodecheckbangalore(pincode):
    regex = "^[5]{1}[6]{1}[02]{1}\\s{0,1}[0-2]{1}[0-9]{2}$"
    pin = re.compile(regex)
    check = re.match(pin,pincode)
    if check is not None:
        return True
    else:
        return False


# Runs the bot
client.run(os.getenv('TOKEN'))
