import discord
from discord.ext import commands
from discord.utils import get
from discord import app_commands
import pickle



intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix = '%', intents=intents)

@bot.event
async def on_ready():
    print("UNBot is Running!")

# UNB ID: 1260736434193567745
# Dev ID: 738985226570825799

#GUILD_ID = discord.Object(id=738985226570825799)
GUILD_ID = discord.Object(id=1260736434193567745)

class VotingGuild:
    def __init__(self, role: discord.Role, membercount: int):
        self.role = role
        self.membercount = membercount

    def __str__(self):
        return self.role.name

    def Count(self):
        return self.membercount

    def Role(self):
        return self.role.mention

class Vote:
    def __init__(self, text: str):
        self.text = text
        self.yays = []
        self.nays = []
        self.abstentions = []

    def __str__(self):
        return self.text

    def Text(self):
        return self.text

    def Yays(self):
        return self.yays

    def Nays(self):
        return self.nays

    def Abstentions(self):
        return self.abstentions

    def addYay(self, user: discord.Member):
        self.yays.append(user)

    def addNay(self, user: discord.Member):
        self.nays.append(user)

    def addAbstention(self, user: discord.Member):
        self.abstentions.append(user)


@bot.tree.command(name="hello", description = "Say hello to UNBot!", guild = GUILD_ID)
async def hello(interaction: discord.Interaction):
    print("Hello Command Run")
    await interaction.response.send_message(f"Hello {interaction.user.mention}! How's it going?", ephemeral=True)

@bot.tree.command(name="printrole", description="Print a list of users with this role", guild = GUILD_ID)
async def hello(interaction: discord.Interaction, role: discord.Role):
    print("Role Check Command Run")
    if role == None:
        print("There is no role like that here")
        await interaction.response.send_message("I'm sorry, but it looks like you asked me to check an invalid role", ephemeral=True)
    else:
        output = ""
        for m in role.members:
            if m.nick != None:
                output += m.nick.title() + ', '
            else:
                output += m.name.title() + ', '
        output = output[0:-2]
        await interaction.response.send_message(f"The following people have the role `{role.name}`: ```{output}```", ephemeral=True)

@bot.command()
async def synccmd(ctx: commands.Context):
    fmt = await bot.tree.sync(guild = GUILD_ID)
    await ctx.send(
        f"Synced {len(fmt)} commands to the current server",
        delete_after = 1.0
    )
    await ctx.message.delete()
    return


bot.run("MTM1MjEwMTUzNjI5NzM5MDEyMQ.GwsMY-.BTt_IzRSiPOtLFa-79sz_dVgtPxQ9Lx9BPbt8s")