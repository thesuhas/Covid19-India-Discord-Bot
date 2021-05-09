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

# Initialising df to something
df = 0
df_daily = 0

# Initialising states list
s = list()

# Initialising slash command
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    global df
    global df_daily
    global s
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
    df_daily.to_csv(file_daily)

    await client.get_channel(810508395546542120).send(f"Bot is online")


@client.event
async def on_guild_join(guild):
    # Create embed to send
    embed = discord.Embed(color=discord.Color.green(), title="Covid19 India Bot",
                          description="Gives various statistics regarding Covid19 in India along with vaccination slots near you")
    embed.add_field(
        name="Hello!", value="Thank you for adding the bot to your server! Use `.help` to find out what commands it currently supports!")

    for channels in guild.text_channels:
        if channels.permissions_for(guild.me).send_messages:
            await channels.send(embed=embed)
            break


@client.event
async def on_message(message):
    if message.author.bot:
        if((message.channel.id == 840644400564142111) and (message.author.id == 836578128305717279)):
            await message.publish()
        else:
            pass
    elif client.user.mentioned_in(message):
        await message.channel.send(f"{message.author.mention} don't ping the bot da lawda")
    else:
        await client.process_commands(message)


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
        4: "Send a review request to any of the following members: `thesuhas`, `RIT3shSapata`, `sach-12` and/or `ArvindAROO`.",
        5: "Wait for approval for reviewers. Your PR may be directly accepted or requested for further changes."
    }
    for ruleNo in rules:
        Embeds.add_field(name='\u200b', value="`" +
                         str(ruleNo) + '`: ' + rules[ruleNo], inline=False)

    stark = ctx.guild.get_member(718845827413442692).mention
    sapota = ctx.guild.get_member(404597472103759872).mention
    suhas = ctx.guild.get_member(554876169363652620).mention
    sach = ctx.guild.get_member(723377619420184668).mention
    Embeds.add_field(name="Reviewers", value="`thesuhas` - {}\n`ArvindAROO` - {}\n `RIT3shSapata` - {} and\n `sach-12` - {}".format(
        suhas, stark, sapota, sach), inline=False)
    Embeds.add_field(
        name="Important", value="**Under no circumstances is anyone allowed to merge to the main branch.**", inline=False)
    await ctx.send(embed=Embeds)


@client.command(aliases=['h', 'help'])
async def help_command(ctx, text=''):
    if text == '':
        embed = discord.Embed(color=discord.Color.green())
        commands = "`.states` to get a list of states\n`.state {state}` to get cases in that particular state\n`.india` to get nationwide cases\n`.vaccine {pincode} {date}` to get vaccination slots near you. If `date` is not mentioned, will take today's date\n`.beds {type of hospital}` to get available beds. Type can be `government/govt` or `private`"
        embed.add_field(name='Commands', value=commands, inline=False)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='help', color=discord.Color.green(
        ), description='`.help` does not take any arguments.\n**Syntax:** `.help`')
        await ctx.send(embed=embed)

# Slash Command of the same


@slash.slash(name="help", description="Commands available from me")
async def help_slash(ctx):
    await ctx.defer()
    help_embed = discord.Embed(color=discord.Color.green())
    commands = "`.states` to get a list of states\n`.state {state}` to get cases in that particular state\n`.india` to get nationwide cases\n`.vaccine {pincode} {date}` to get vaccination slots near you. If `date` is not mentioned, will take today's date\n`.beds {type of hospital}` to get available beds. Type can be `government/govt` or `private`(Only Bengaluru)"
    help_embed.add_field(name='Commands', value=commands, inline=False)
    await ctx.send(embeds=[help_embed])


@client.command(aliases=['state'])
async def state_command(ctx, *, state=''):
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
    await ctx.send(embeds=[embed])


@client.command()
async def states(ctx, text=''):
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
                # print(i)
                # Look at all sessions
                for j in i['sessions']:
                    # If there is an available session
                    if j['available_capacity'] >= 1:
                        # Check if hospital exists
                        if i['name'] in sessions:
                            sessions[i['name']].append(j)
                        else:
                            sessions[i['name']] = list()
                            sessions[i['name']].append(j)
            if len(sessions) == 0:
                await ctx.send("No available sessions")
            else:
                # Create an embed for every session
                for sesh in sessions:
                    embed = discord.Embed(
                        title=f"Vaccine Available at {sesh}", color=discord.Color.green())
                    embed.add_field(name='Date', value=date, inline=False)
                    embed.add_field(
                        name='Available Capacity', value=sessions[sesh][0]['available_capacity'], inline=False)
                    embed.add_field(
                        name='Minimum Age', value=sessions[sesh][0]['min_age_limit'], inline=False)
                    embed.add_field(
                        name='Vaccine', value=sessions[sesh][0]['vaccine'])
                    embed.add_field(name="Slots", value='\n'.join(
                        sessions[sesh][0]['slots']), inline=False)
                    await ctx.send(embed=embed)
        else:
            await ctx.send("No available vaccination center")


@slash.slash(name='vaccine', description='List of Vaccination slots near you')
async def vaccine_slash(ctx, pincode="", date=datetime.datetime.now().strftime("%d-%m-%Y")):
    await ctx.defer()
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
                # print(i)
                # Look at all sessions
                for j in i['sessions']:
                    # If there is an available session
                    if j['available_capacity'] >= 1:
                        # Check if hospital exists
                        if i['name'] in sessions:
                            sessions[i['name']].append(j)
                        else:
                            sessions[i['name']] = list()
                            sessions[i['name']].append(j)
            if len(sessions) == 0:
                await ctx.send("No available sessions")
            else:
                # Create an embed for every session
                for sesh in sessions:
                    embed = discord.Embed(
                        title=f"Vaccine Available at {sesh}", color=discord.Color.green())
                    embed.add_field(name='Date', value=date, inline=False)
                    embed.add_field(
                        name='Available Capacity', value=sessions[sesh][0]['available_capacity'], inline=False)
                    embed.add_field(
                        name='Minimum Age', value=sessions[sesh][0]['min_age_limit'], inline=False)
                    embed.add_field(
                        name='Vaccine', value=sessions[sesh][0]['vaccine'])
                    embed.add_field(name="Slots", value='\n'.join(
                        sessions[sesh][0]['slots']), inline=False)
                    await ctx.send(embed=embed)
        else:
            await ctx.send("No available vaccination center")


@tasks.loop(seconds=86400)
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


@tasks.loop(seconds=300)
async def alert():
    date = datetime.datetime.now().strftime("%d-%m-%Y")
    datetom = (datetime.datetime.now() +
               datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    dates = [date, datetom]
    d_ids = [276, 265, 294]
    for i in dates:
        for j in d_ids:
            headers = {"Accept-Language": "en-IN",
                       'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            data = {"district_id": j, "date": i}
            res = requests.get(
                "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict", headers=headers, params=data)
            #resp = res.json()
            print(res.status_code)
            if(res.status_code == 200):
                resp = res.json()
                for k in resp['sessions']:
                    if(len(k) != 0):
                        if(k['available_capacity'] > 0 and k['min_age_limit'] == 18):
                            embed = discord.Embed(
                                title=f"Vaccine Available at {k['name']}", color=discord.Color.green())
                            embed.add_field(
                                name='Date', value=k['date'], inline=False)
                            embed.add_field(
                                name='Available Capacity', value=k['available_capacity'], inline=False)
                            embed.add_field(
                                name='Minimum Age', value=k['min_age_limit'], inline=False)
                            embed.add_field(
                                name='Vaccine', value=k['vaccine'])
                            embed.add_field(name="Slots", value='\n'.join(
                                k['slots']), inline=False)
                            await client.get_channel(840644400564142111).send(embed=embed)
                    else:
                        continue
            else:
                continue


# Runs the bot
client.run(os.getenv('TOKEN'))
