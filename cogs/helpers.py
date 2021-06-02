from discord.ext import commands
import re

class Helpers(commands.Cog):

    def __init__(self, client):
        self.client = client

    def pincodecheckindia(pincode):
        regex = "^[1-9]{1}[0-9]{2}\\s{0,1}[0-9]{3}$"
        pin = re.compile(regex)
        check = re.match(pin, pincode)
        if check is not None:
            return True
        else:
            return False

    def pincodecheckbangalore(pincode):
        regex = "^[5]{1}[6]{1}[02]{1}\\s{0,1}[0-2]{1}[0-9]{2}$"
        pin = re.compile(regex)
        check = re.match(pin, pincode)
        if check is not None:
            return True
        else:
            return False

    
def setup(client):
    client.add_cog(Helpers(client))