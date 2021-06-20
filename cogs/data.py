import discord
from discord.ext import commands, tasks
from discord_slash import cog_ext
import pandas as pd
import requests
from babel.numbers import format_currency
import datetime
import io


class Data(commands.Cog):
    # Initialisation command
    def __init__(self, client):
        self.client = client

        # Filenames for updation
        self.filename = 'data/states.csv'
        self.file_daily = 'data/states_yesterday.csv'

        # Mapping for queries to states_yesterday
        self.mapp = {"total": 'TT', 'andaman and nicobar islands': 'AN', "andhra pradesh": 'AP', "arunachal pradesh": 'AR', "assam": 'AS', "bihar": 'BR', "chandigarh": 'CH', "chhattisgarh": 'CT', "dadra and nagar haveli and daman and diu": 'DN', "dadra and nagar haveli and daman and diu": 'DD', "delhi": 'DL', "goa": 'GA', "gujarat": 'GJ', "haryana": 'HR', "himachal pradesh": 'HP', "jammu and kashmir": 'JK', "jharkhand": 'JH',
                     "karnataka": 'KA', "kerala": 'KL', "ladakh": 'LA', "lakshadweep": 'LD', "madhya pradesh": 'MP', "maharashtra": 'MH', "manipur": 'MN', "meghalaya": 'ML', "mizoram": 'MZ', "nagaland": 'NL', "odisha": 'OR', "puducherry": 'PY', "punjab": 'PB', "rajasthan": 'RJ', "sikkim": 'SK', "tamil nadu": 'TN', "telangana": 'TG', "tripura": 'TR', "uttar pradesh": 'UP', "uttarakhand": 'UT', "west bengal": 'WB', "state unassigned": 'UN'}

        # Initialising dfs
        self.df = 0
        self.df_daily = 0

        # Initialising footer
        self.footer = 0

        # Initialising states list
        self.s = list()

    # on_ready
    @commands.Cog.listener()
    async def on_ready(self):

        # Starting loops
        self.update.start()
        self.update_daily.start()
        # cowin.Cowin.alert.start()
        # cowin.Cowin.clear.start()

        test = requests.get(
            'https://api.covid19india.org/csv/latest/state_wise.csv')
        test = str(test.text)

        data = io.StringIO(test)
        df = pd.read_csv(data, sep=",")
        # Create states list
        self.s = [df.iloc[i]['State'] for i in range(len(df))]
        # Removing Total and State Unassigned
        self.s = self.s[1:len(self.s) - 1]
        # Making column lower case
        df["State"] = df["State"].str.lower()
        df.to_csv(self.filename)
        # Assigning df to self
        self.df = df
        print("df Updated at: ", datetime.datetime.now())
        time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
        time = time.strftime("%d-%b") + ' at ' + time.strftime("%I:%M %p")
        self.footer = f"Last Updated: {time}"

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
            df_daily.to_csv(self.file_daily)
            # Assigning df_daily
            self.df_daily = df_daily
            print("df_daily Updated at: ", datetime.datetime.now())

        activity = discord.Activity(
            name="Plague Inc.", type=discord.ActivityType.playing)
        await self.client.change_presence(activity=activity)
        await self.client.get_channel(841561036305465344).send(f"Bot is online")

    @commands.command(aliases=['state'])
    async def state_command(self, ctx, *, state=''):
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
                entry = self.df.loc[self.df['State'] == state.lower()]
                if entry.empty:
                    await ctx.send("Chosen state not available")
                else:
                    #m = f"**Covid Cases in {state[0].upper() + state[1:]}:**\nConfirmed: {entry['Confirmed'].values[0]}\nRecovered: {entry['Recovered'].values[0]}\nDeaths: {entry['Deaths'].values[0]}\nActive: {entry['Active'].values[0]}"
                    embed = discord.Embed(
                        title=f"Cases in {state[0].upper() + state[1:]}", color=discord.Color.green())
                    embed.add_field(name='Active', value=format_currency(
                        int(entry['Active'].values[0]), 'INR', locale='en_IN')[1:-3], inline=False)
                    embed.add_field(name='Confirmed', value=format_currency(int(entry['Confirmed'].values[0]), 'INR', locale='en_IN')[
                                    1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Confirmed'][self.mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                    embed.add_field(name='Recovered', value=format_currency(int(entry['Recovered'].values[0]), 'INR', locale='en_IN')[
                                    1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Recovered'][self.mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                    embed.add_field(name='Deaths', value=format_currency(int(entry['Deaths'].values[0]), 'INR', locale='en_IN')[
                                    1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Deceased'][self.mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                    embed.set_footer(text=self.footer)
                    await ctx.send(embed=embed)

    @cog_ext.cog_slash(name='state', description='State-wise stats of COVID-19')
    async def state_slash(self, ctx, *, state=''):
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
                entry = self.df.loc[self.df['State'] == state.lower()]
                if entry.empty:
                    await ctx.send("Chosen state not available")
                else:
                    #m = f"**Covid Cases in {state[0].upper() + state[1:]}:**\nConfirmed: {entry['Confirmed'].values[0]}\nRecovered: {entry['Recovered'].values[0]}\nDeaths: {entry['Deaths'].values[0]}\nActive: {entry['Active'].values[0]}"
                    embed = discord.Embed(
                        title=f"Cases in {state[0].upper() + state[1:]}", color=discord.Color.green())
                    embed.add_field(name='Active', value=format_currency(
                        int(entry['Active'].values[0]), 'INR', locale='en_IN')[1:-3], inline=False)
                    embed.add_field(name='Confirmed', value=format_currency(int(entry['Confirmed'].values[0]), 'INR', locale='en_IN')[
                                    1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Confirmed'][self.mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                    embed.add_field(name='Recovered', value=format_currency(int(entry['Recovered'].values[0]), 'INR', locale='en_IN')[
                                    1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Recovered'][self.mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                    embed.add_field(name='Deaths', value=format_currency(int(entry['Deaths'].values[0]), 'INR', locale='en_IN')[
                                    1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Deceased'][self.mapp[state]]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
                    embed.set_footer(text=self.footer)
                    await ctx.send(embed=embed)

    @commands.command(aliases=['india'])
    async def india_command(self, ctx):
        entry = self.df.loc[self.df['State'] == 'total']
        #m = f"**Covid Cases in the country:**\nConfirmed: {entry['Confirmed'].values[0]}\nRecovered: {entry['Recovered'].values[0]}\nDeaths: {entry['Deaths'].values[0]}\nActive: {entry['Active'].values[0]}"
        embed = discord.Embed(title="Cases in the Country",
                              color=discord.Color.green())
        embed.add_field(name='Active', value=format_currency(
            int(entry['Active'].values[0]), 'INR', locale='en_IN')[1:-3], inline=False)
        embed.add_field(name='Confirmed', value=format_currency(int(entry['Confirmed'].values[0]), 'INR', locale='en_IN')[
                        1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Confirmed'][self.mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
        embed.add_field(name='Recovered', value=format_currency(int(entry['Recovered'].values[0]), 'INR', locale='en_IN')[
                        1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Recovered'][self.mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
        embed.add_field(name='Deaths', value=format_currency(int(entry['Deaths'].values[0]), 'INR', locale='en_IN')[
                        1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Deceased'][self.mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
        embed.set_footer(text=self.footer)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name='india', description='Stats of COVID-19 in India')
    async def india_slash(self, ctx):
        await ctx.defer()
        entry = self.df.loc[self.df['State'] == 'total']
        embed = discord.Embed(title="Cases in the Country",
                              color=discord.Color.green())
        embed.add_field(name='Active', value=format_currency(
            int(entry['Active'].values[0]), 'INR', locale='en_IN')[1:-3], inline=False)
        embed.add_field(name='Confirmed', value=format_currency(int(entry['Confirmed'].values[0]), 'INR', locale='en_IN')[
                        1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Confirmed'][self.mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
        embed.add_field(name='Recovered', value=format_currency(int(entry['Recovered'].values[0]), 'INR', locale='en_IN')[
                        1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Recovered'][self.mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
        embed.add_field(name='Deaths', value=format_currency(int(entry['Deaths'].values[0]), 'INR', locale='en_IN')[
                        1:-3] + '\n(+' + format_currency(int(self.df_daily[self.df_daily['Status'] == 'Deceased'][self.mapp['total']]), 'INR', locale='en_IN')[1:-3] + ')', inline=False)
        embed.set_footer(text=self.footer)
        await ctx.send(embeds=[embed])

    @commands.command(aliases=['states'])
    async def states_command(self, ctx, text=''):
        if text != '':
            await ctx.send('Wrong usage of command, check `.help`')
        else:
            # Returns list of states
            string = '**States and Union Territories:\n**'
            for i in self.s:
                string += i + '\n'
            await ctx.send(string)

    @tasks.loop(seconds=1800)
    async def update_daily(self):
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
            df_daily.to_csv(self.file_daily)
            self.df_daily = df_daily
            print("df_daily Updated at: ", datetime.datetime.now())

    @tasks.loop(seconds=1800)
    async def update(self):
        # Create basic data frame and store
        test = requests.get(
            'https://api.covid19india.org/csv/latest/state_wise.csv')
        test = str(test.text)

        data = io.StringIO(test)
        df = pd.read_csv(data, sep=",")
        # Making states lowercase
        df["State"] = df["State"].str.lower()
        df.to_csv(self.filename)
        # Assign df
        self.df = df
        # Prints when df is last updated
        print("df Updated at: ", datetime.datetime.now())
        time = datetime.datetime.now() + datetime.timedelta(hours=5, minutes=30)
        time = time.strftime("%d-%b") + ' at ' + time.strftime("%I:%M %p")
        self.footer = f"Last Updated: {time}"


def setup(client):
    client.add_cog(Data(client))
