import discord
from discord.ext import commands, tasks
import requests
import datetime
import math
import os
import re


class Cowin(commands.Cog):
    # Initialisation
    def __init__(self, client):
        self.client = client

        # URLs
        self.url1 = os.getenv('url1')
        self.url2 = os.getenv('url2')
        self.url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict"

    @commands.command(aliases=['vaccine'])
    async def vaccine_command(self, ctx, pincode="", date=datetime.datetime.now().strftime("%d-%m-%Y")):
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

    @tasks.loop(seconds=20)
    async def alert(self):
        date = datetime.datetime.now().strftime("%d-%m-%Y")
        datetom = (datetime.datetime.now() +
                datetime.timedelta(days=1)).strftime("%d-%m-%Y")
        dates = [date, datetom]
        d_ids = [276, 265, 294]
        for j in d_ids:
            if(j == 276):
                url = self.url1
            if(j == 265):
                url = self.url2
            if(j == 294):
                url = self.url
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
                                fp = open('alerts.csv', 'r')
                                fp2 = open('mypings.csv', 'r')
                                ch_list = [line.split(',')[1] for line in list(
                                    filter(None, fp.read().split('\n')))]
                                for ch in ch_list:
                                    await self.client.get_channel(int(ch)).send(embed=embed)
                                    try:
                                        for line in fp2:
                                            p_codes = line.replace('\n', '').split(',')[2]
                                            file_guild_ids = line.split(',')[1]
                                            channel_guild_id = self.client.get_channel(int(ch)).guild.id
                                            if((str(k['pincode']) in p_codes) and (str(channel_guild_id) in file_guild_ids)):
                                                member_id = int(line.split(',')[0])
                                                memberObj =self. client.get_user(member_id)
                                                await self.client.get_channel(int(ch)).send(memberObj.mention)
                                    except Exception as e:
                                        continue
                                #await client.get_channel(841561036305465344).send(embed=embed)
                                fp.close()
                                fp2.close()
                        else:
                            continue
                else:
                    continue

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


def setup(client):
    client.add_cog(Cowin(client))