import discord
from discord.ext import commands, menus

class Events(commands.Cog):

    def __init__(self, client):
        self.client = client

    #Events


    #Commands
    '''@commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")'''

def setup(client):
    client.add_cog(Events(client))