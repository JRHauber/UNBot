import enum
import discord
from discord.ext import commands
from discord import app_commands
import pickle

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix = '%', intents=intents)

class Responses(enum.Enum):
    yay = 1
    nay = 2
    abstain = 3

class VotingGuild:
    def __init__(self, role: int, membercount: int, delegatecount: int):
        self.role = role
        self.membercount = membercount
        self.delegatecount = delegatecount

    def __str__(self):
        return self.role

    def Count(self):
        return self.membercount

    def Role(self):
        return self.role

    def Delegates(self):
        return self.delegatecount

    def SetCount(self, count: int):
        self.membercount = count
        return(f"Member count set to: {self.membercount}")

    def SetDelegates(self, count: int):
        self.delegatecount = count
        return(f"Delegate count set to: {self.delegatecount}")

class Vote:
    def __init__(self, name: str, text: str):
        self.text = text
        self.name = name
        self.votes = {}

    def __str__(self):
        return self.text

    def Text(self):
        return self.text

    def Name(self):
        return self.name

    def Votes(self):
        return self.votes

    def AddVote(self, user: int, vote: Responses):
        self.votes[user] = vote

async def send_long_message(interaction: discord.Interaction, text: str, ephem: bool):
    MAX_LENGTH = 2000
    if len(text) <= MAX_LENGTH:
        await interaction.response.send_message(text, ephemeral=ephem)
    else:
        chunks = [text[i:i + MAX_LENGTH] for i in range(0, len(text), MAX_LENGTH)]
        for chunk in chunks:
            await interaction.response.send_message(chunk, ephemeral=ephem)

try:
    votes = pickle.load(open("votes.p", "rb"))
except FileNotFoundError:
    votes = []

try:
    guilds = pickle.load(open("guilds.p", "rb"))
except FileNotFoundError:
    guilds = []

@bot.event
async def on_ready():
    print("UNBot is Running!")

# UNB ID: 1260736434193567745
# Dev ID: 738985226570825799

#GUILD_ID = discord.Object(id=738985226570825799)
GUILD_ID = discord.Object(id=1260736434193567745)

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

@bot.tree.command(name="guild_update", description = "Update guild information for voting", guild = GUILD_ID)
@app_commands.rename(count = "members")
@app_commands.rename(count2 = "delegates")
@app_commands.describe(count = "Number of Members in group")
@app_commands.describe(count2 = "Number of Delegates in group")
@app_commands.checks.has_role(1348752459287367730)
async def guildupdate(interaction: discord.Interaction, role: discord.Role, count: int, count2: int):
    for g in guilds:
        if g.Role() == role.id:
            await interaction.response.send_message(g.SetCount(count) + " - " + g.SetDelegates(count2), ephemeral = True)
            pickle.dump(guilds, open("guilds.p", "wb"))
            return
    temp = VotingGuild(role.id, count, count2)
    guilds.append(temp)
    await interaction.response.send_message(temp.SetCount(count) + " - " + temp.SetDelegates(count2), ephemeral = True)
    pickle.dump(guilds, open("guilds.p", "wb"))

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("Sorry, you don't have the right role to run that command", ephemeral=True)

@bot.tree.command(name="guild_check", description = "Check all guild data", guild = GUILD_ID)
@app_commands.checks.has_role(1348752459287367730)
async def guildcheck(interaction: discord.Interaction):
    output = "```\n"
    for g in guilds:
        for r in interaction.guild.roles:
            if r.id == g.Role():
                name = r.name
        mem_count = g.Count()
        del_count = g.Delegates()
        output += f"{name} - Members: {mem_count} - Delegates: {del_count}\n"
    output += "```"
    await interaction.response.send_message(output, ephemeral=True)

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("Sorry, you don't have the right role to run that command", ephemeral=True)

@bot.tree.command(name="guild_count", description = "See the # of members for each guild", guild = GUILD_ID)
@app_commands.checks.has_role(1348752459287367730)
async def guildcount(interaction: discord.Interaction, role: discord.Role):
    for g in guilds:
        if g.Role() == role.id:
            await interaction.response.send_message(f"The guild {g.Role()} has `{g.Count()}` members.", ephemeral=True)

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("Sorry, you don't have the right role to run that command", ephemeral=True)

@bot.tree.command(name="create_vote", description = "Create a vote", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def createvote(interaction: discord.Interaction, name: str, text: str):
    v = Vote(name, text)
    votes.append(v)
    pickle.dump(votes, open("votes.p", "wb"))
    await interaction.response.send_message(f'''
    > # {v.name}
    > ### {v.text}
    ''')

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("Sorry, you don't have the right role to run that command", ephemeral=True)

@bot.tree.command(name="vote", description="cast your vote", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def vote(interaction:discord.Interaction, vote: str, choice: Responses):
    for v in votes:
        if v.Name().title() == vote.title():
            v.AddVote(interaction.user.id, choice)
            if choice is Responses.yay:
                await interaction.response.send_message("Your yes vote has been recorded.", ephemeral = True)
                pickle.dump(votes, open("votes.p", "wb"))
                return
            if choice is Responses.nay:
                await interaction.response.send_message("Your no vote has been recorded.", ephemeral = True)
                pickle.dump(votes, open("votes.p", "wb"))
                return
            if choice is Responses.abstain:
                await interaction.response.send_message("Your abstain vote has been recorded.", ephemeral = True)
                pickle.dump(votes, open("votes.p", "wb"))
                return
    await interaction.response.send_message("Sorry, it doesn't look like there's a vote with that name. Please try again.", ephemeral = True)
    return

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("Sorry, you don't have the right role to run that command", ephemeral=True)

@bot.tree.command(name="listvotes", description="list active votes", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def list_votes(interaction:discord.Interaction):
    output = '```'
    for v in votes:
        output += v.Name() + ' \n'
    output += '```'
    await interaction.response.send_message(output, ephemeral=True)

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("Sorry, you don't have the right role to run that command", ephemeral=True)

@bot.tree.command(name="tally", description = "tally a vote", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def tally(interaction: discord.Interaction, name: str):
    await interaction.response.defer(ephemeral=True)
    yay_total_power = 0.0
    yay_total = 0
    nay_total_power = 0.0
    nay_total = 0
    abs_total_power = 0.0
    abs_total = 0
    total_power = 0.0
    total = 0
    for v in votes:
        if v.Name().title() == name.title():
            yay_output = "```\nYays: \n"
            nay_output = "```\nNays: \n"
            abs_output = "```\nAbstain: \n"
            for g in guilds:
                total += g.Delegates()
                total_power += g.Count()
            for k, v in v.Votes().items():
                if v is Responses.yay:
                    user = interaction.guild.get_member(k)
                    for g in guilds:
                        for r in interaction.guild.roles:
                            if r in user.roles and r.id == g.Role():
                                user_power = float(g.Count())/float(g.Delegates())
                                yay_total += 1
                                yay_total_power += user_power
                                if user.nick != None:
                                    yay_output += f"{user.nick} - 1 - {str(user_power)}\n"
                                else:
                                    yay_output += f"{user.name.title()} - 1 - {str(user_power)}\n"
                if v is Responses.nay:
                    user = interaction.guild.get_member(k)
                    for g in guilds:
                        for r in interaction.guild.roles:
                            if r in user.roles and r.id == g.Role():
                                user_power = float(g.Count())/float(g.Delegates())
                                nay_total += 1
                                nay_total_power += user_power
                                if user.nick != None:
                                    nay_output += f"{user.nick} - 1 - {str(user_power)}\n"
                                else:
                                    nay_output += f"{user.name.title()} - 1 - {str(user_power)}\n"
                if v is Responses.abstain:
                    user = interaction.guild.get_member(k)
                    for g in guilds:
                        for r in interaction.guild.roles:
                            if r in user.roles and r.id == g.Role():
                                user_power = float(g.Count())/float(g.Delegates())
                                abs_total += 1
                                abs_total_power += user_power
                                if user.nick != None:
                                    abs_output += f"{user.nick} - 1 - {str(user_power)}\n"
                                else:
                                    abs_output += f"{user.name.title()} - 1 - {str(user_power)}\n"
    if total == 0:
        await interaction.followup.send("Sorry, doesn't look like there's a vote with that name.", ephemeral=True)
        return
    if float((abs_total + nay_total + yay_total)) >= (0.6 * total):
        await interaction.followup.send("There are enough participating delegates, the vote is valid.", ephemeral=True)
        yay_output += f"\nDelegate Vote: {yay_total}/{total} ({float((yay_total)/float(total))*100.0:.2f}%)\n"
        yay_output += f"Population Vote: {yay_total_power}/{total_power} ({(yay_total_power/total_power)*100.0:.2f}%)\n```"
        nay_output += f"\nDelegate Vote: {nay_total}/{total} ({float((nay_total)/float(total))*100.0:.2f}%)\n"
        nay_output += f"Population Vote: {nay_total_power}/{total_power} ({(nay_total_power/total_power)*100.0:.2f}%)\n```"
        abs_output += f"\nDelegate Vote: {abs_total}/{total} ({float((abs_total)/float(total))*100.0:.2f}%)\n"
        abs_output += f"Population Vote: {abs_total_power}/{total_power} ({(abs_total_power/total_power)*100.0:.2f}%)\n```"
        await interaction.followup.send(yay_output)
        await interaction.followup.send(nay_output)
        await interaction.followup.send(abs_output)
    else:
        await interaction.followup.send("There aren't enough participating delegates, this is an invalid vote.", ephemeral=True)
        return

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("Sorry, you don't have the right role to run that command", ephemeral=True)

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