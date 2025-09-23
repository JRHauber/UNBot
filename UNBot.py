import enum
import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks
import pickle
import json
import asyncio
import datetime
import database_sqlite
import math

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
GENERAL_ASSEMBLY = None
class MyBot(commands.Bot):
    async def setup_hook(self):
        census_loop.start()
        handle_proposal.start()

bot = MyBot(command_prefix='%', intents=intents)

census_time = datetime.time(hour = 0, minute = 0, second = 0)

db = database_sqlite.DatabaseSqlite()
db.setup_db()

class Responses(enum.Enum):
    yay = 1
    nay = -1
    abstain = 0

class VotingGuild:
    def __init__(self, name: str, role: int, membercount: int, delegatecount: int):
        self.name = name
        self.role = role
        self.membercount = membercount
        self.delegatecount = delegatecount
        self.serverid = 0
        self.citizenrole = 0

    def __str__(self):
        return self.role

    def Count(self):
        return self.membercount

    def Role(self):
        return self.role

    def Delegates(self):
        return self.delegatecount

    def Server(self):
        return self.serverid

    def CitizenRole(self):
        return self.citizenrole

    def Name(self):
        return self.name

    def SetCount(self, count: int):
        self.membercount = count
        return(f"Member count set to: {self.membercount}")

    def SetDelegates(self, count: int):
        self.delegatecount = count
        return(f"Delegate count set to: {self.delegatecount}")

    def SetServer(self, server: int):
        self.serverid = server
        return(f"Server id set to {self.serverid}")

    def SetCitizen(self, role: int):
        self.citizenrole = role
        return(f"Citizen role set to {self.citizenrole}")

class Vote:
    def __init__(self, name: str, text: str, id: int, start: float, discuss: float, vote: float):
        self.text = text
        self.name = name
        self.votes = {}
        self.id = id
        self.completed = False
        self.start_time = start
        self.discuss_time = discuss
        self.vote_time = vote

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

    def Complete(self):
        self.completed = True

@bot.event
async def on_guild_channel_create(channel):
    if "ticket" in channel.name.lower() and channel.guild.id == GUILD_ID.id:
        await asyncio.sleep(2)
        await channel.send("""
            Hello! Thank you for creating a ticket to have your group join the United Nations of Bitcraft. If you did this in error, please click the close ticket button.
            To help expedite the process, please answer the following questions to verify you meet the requirements for membership.
            1) What is the name of your group?
            2) What is the link to your discord server?
            3) Does your group have 25 Unique Members? (i.e, members that are not already in another UNB group)
            4) Please share an image/explain your groups defined leadership structure.
            5) How old is your group?
            6) Are you in any ongoing conflicts with other groups?
            7) If the answers to the above questions are yes, who are your delegates you'll be sending? Delegates must be leaders of the group and you can send up to 3. Delegates must be at least 18 years old.
            8) Do you want to send a moderator? Moderates must be non-leaders and each group can send 1. Moderators must be at least 18 years old.
            """)

@bot.event
async def on_member_join(member):
    if member.guild.id == GUILD_ID.id:
        guild_list = ""
        for g in guilds:
            guild_list += member.guild.get_role(g.Role()).name + ", "
        guild_list = guild_list[:-2]
        await asyncio.sleep(5)
        await member.send(f"""
            Greetings! Welcome to the United Nations of Bitcraft Discord server!
            You will automatically be granted the observer role upon joining the server.
            If you are a in one of our member groups, please head to this channel to get your role: https://discord.com/channels/1260736434193567745/1364546829466996757
            The current member groups are: {guild_list}.
            There will also be other roles to collect in the channel, please be sure to check those out and check back in periodicially to see if new roles you may be interested in are available.
            Regards,
            The UNB Team
        """)
        print(f"Sent welcome message to {member.name}")
    return

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    UNB = await bot.fetch_guild(1260736434193567745)
    delegate = UNB.get_role(1348752329964388383)
    guild_list = await db.get_guilds()

    if delegate in after.roles and not delegate in before.roles:
        for g in guild_list:
            g_role = UNB.get_role(g[0])
            if g_role in after.roles:
                await db.add_delegate(after.id, g[0])
    if delegate in before.roles and not delegate in after.roles:
        await db.remove_delegate(after.id)

@bot.event
async def on_thread_create(thread: discord.Thread):
    await thread.join()
    await discord.utils.sleep_until(datetime.datetime.now() + datetime.timedelta(seconds=5))
    if thread.parent_id == 1348753509121789952:
        time = datetime.datetime.now() + datetime.timedelta(hours=48)
        await db.add_proposal(thread.name, thread.starter_message.content, time.timestamp())
        await GENERAL_ASSEMBLY.send(f"""
        <@&1348752329964388383>
        A new proposal has been created! Discussion for this proposal will go for 48 hours.
        The proposal can be found here: {thread.jump_url}
        Discussion for this proposal will end <t:{int(time.timestamp())}:R> on <t:{int(time.timestamp())}:F>
        """)
        if not handle_proposal.is_running():
            handle_proposal.start()

try:
    guilds = pickle.load(open("guilds.p", "rb"))
except FileNotFoundError:
    guilds = []

with open('config.json', 'r') as f:
    config = json.load(f)
    TOKEN = config['token']

@bot.event
async def on_ready():
    global GENERAL_ASSEMBLY
    GENERAL_ASSEMBLY = bot.get_guild(1260736434193567745).get_channel(1348751860030246963)
    print("UNBOT IS READY")

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
    count = 0
    if role == None:
        await interaction.response.send_message("I'm sorry, but it looks like you asked me to check an invalid role", ephemeral=True)
    else:
        output = ""
        for m in role.members:
            count += 1
            output += m.display_name+ ", "
        output = output[0:-2]
        await interaction.response.send_message(f"The following people have the role `{role.name}`: ```{output}``` ({count})", ephemeral=True)

@bot.tree.command(name="create_guild", description = "create a guild", guild = GUILD_ID)
@app_commands.checks.has_role(1260736434193567745)
async def create_guild(interaction: discord.Interaction, role : discord.Role):
    await interaction.response.defer(ephemeral=True)
    await db.add_guild(role.id)
    await interaction.followup.send(f"Created a new guild with id: {role.id} and name: {role.name}")

@bot.tree.command(name="vote", description="cast your vote", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def vote(interaction:discord.Interaction, proposal_id: int, choice: Responses):
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("Casting your vote!", ephemeral = True)
    data = await db.get_proposal(proposal_id)
    if data[3] == 1:
        await interaction.followup.send("This vote is no longer active and cannot be voted on", ephemeral = True)
        print(f"{interaction.user.display_name}'s vote failed the active vote check on proposal {proposal_id}")
        return
    if choice is Responses.yay:
        await db.add_vote(proposal_id, interaction.user.id, choice.value)
        await interaction.followup.send("Your yes vote has been recorded.", ephemeral = True)
        print(f"{interaction.user.display_name} voted yay on proposal {proposal_id}.")
        await db.activate_delegate(interaction.user.id)
        return
    if choice is Responses.nay:
        await db.add_vote(proposal_id, interaction.user.id, choice.value)
        await interaction.followup.send("Your no vote has been recorded.", ephemeral = True)
        print(f"{interaction.user.display_name} voted nay on proposal {proposal_id}.")
        await db.activate_delegate(interaction.user.id)
        return
    if choice is Responses.abstain:
        await db.add_vote(proposal_id, interaction.user.id, choice.value)
        await interaction.followup.send("Your abstain vote has been recorded.", ephemeral = True)
        print(f"{interaction.user.display_name} voted abs on proposal {proposal_id}.")
        await db.activate_delegate(interaction.user.id)
        return
    print(f"{interaction.user.display_name}'s vote failed all checks")
    await interaction.followup.send("Sorry, it doesn't look like there's a vote with that name. Please try again.", ephemeral = True)
    return

@bot.tree.command(name="listvotes", description="list active votes", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def list_votes(interaction:discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    data = await db.get_active_proposals()
    output = "```"
    v_output = "Not Voted"
    for d in data:
        votes = await db.get_votes(d[1])
        for v in votes:
            if v[1] == interaction.user.id:
                match v[2]:
                    case 1:
                        v_output = "Yay"
                        break
                    case -1:
                        v_output = "Nay"
                        break
                    case 0:
                        v_output = "Abs"
                        break
                    case _:
                        v_output = "Error"
                        break
        if len(d[0]) > 30:
            name = d[0][:27] + "..."
        else:
            name = d[0]
        output += f"{name:30} - {d[1]:4} - {v_output}\n"
    output += "\n```"
    await interaction.followup.send(output, ephemeral=True)

@bot.tree.command(name="tally", description = "tally a vote", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def tally(interaction: discord.Interaction, id: int):
    await interaction.response.defer(ephemeral=True)
    print(f"{interaction.user.display_name} ran the tally command")
    log_channel = interaction.guild.get_channel(1398987542476619786)
    yay_total_power = 0.0
    yay_total = 0
    nay_total_power = 0.0
    nay_total = 0
    abs_total_power = 0.0
    abs_total = 0
    total = 0
    delegate_list = await db.get_delegates()
    #Initialize Output Strings
    yay_output = "```\nYays: \n\n"
    nay_output = "```\nNays: \n\n"
    abs_output = "```\nAbstain: \n\n"

    total = len(delegate_list)

    # Loop through all votes for this Proposal
    data = await db.get_votes(id)
    proposal = await db.get_proposal(id)
    for d in data:
        # Skip if vote is set to default value
        if d[2] == -2:
            continue

        # Yay vote processing
        if d[2] == 1:
            for x in delegate_list:
                if x[0] == d[1]:
                    yay_total += 1
                    yay_total_power += x[4]
                    user = await bot.get_user(x[0])
                    yay_output += f"{user.display_name:<20} - {x[4]:.2f}\n"

        # Nay vote Processing
        if d[2] == -1:
            for x in delegate_list:
                if x[0] == d[1]:
                    nay_total += 1
                    nay_total_power += x[4]
                    user = await bot.get_user(x[0])
                    nay_output += f"{user.display_name:<20} - {x[4]:.2f}\n"

        # Abstain vote Processing
        if d[2] == 0:
            for x in delegate_list:
                if x[0] == d[1]:
                    abs_total += 1
                    abs_total_power += x[4]
                    user = await bot.get_user(x[0])
                    abs_output += f"{user.display_name:<20} - {x[4]:.2f}\n"

    if float((abs_total + nay_total + yay_total)) >= math.floor((0.5 * total)):
        present_total = yay_total + abs_total + nay_total
        present_total_power = yay_total_power + abs_total_power + nay_total_power
        await interaction.followup.send("There are enough participating delegates, the vote is valid.")
        yay_output += f"\nDelegate Vote: {yay_total}/{present_total} ({float((yay_total)/float(present_total))*100.0:.2f}%)\n"
        yay_output += f"Population Vote: {yay_total_power} ({(yay_total_power/present_total_power)*100.0:.2f}%)\n```"
        nay_output += f"\nDelegate Vote: {nay_total}/{present_total} ({float((nay_total)/float(present_total))*100.0:.2f}%)\n"
        nay_output += f"Population Vote: {nay_total_power} ({(nay_total_power/present_total_power)*100.0:.2f}%)\n```"
        abs_output += f"\nDelegate Vote: {abs_total}/{present_total} ({float((abs_total)/float(present_total))*100.0:.2f}%)\n"
        abs_output += f"Population Vote: {abs_total_power} ({(abs_total_power/present_total_power)*100.0:.2f}%)\n```"
        await interaction.followup.send(yay_output)
        await interaction.followup.send(nay_output)
        await interaction.followup.send(abs_output)
        await db.complete_vote(id)
        if yay_total/present_total > 0.5 and yay_total_power/present_total_power > 0.6:
            output = f"""
            The Proposal {proposal[1]} ({proposal[0]}) passed on <t:{int(datetime.datetime.now().timestamp())}:F>.
            """
            await log_channel.send(output)
        else:
            output = f"""
            The Proposal {proposal[1]} ({proposal[0]}) failed on <t:{int(datetime.datetime.now().timestamp())}:F>.
            """
            await log_channel.send(output)
    else:
        await interaction.followup.send("There aren't enough participating delegates, this is an invalid vote.", ephemeral=True)
        await db.complete_vote(id)
        output = f"""
            The Proposal {proposal[1]} ({proposal[0]}) failed due to lack of votes on <t:{int(datetime.datetime.now().timestamp())}:F>.
            """
        await log_channel.send(output)
    all_delegates = await db.get_all_delegates()
    for d in all_delegates:
        if not d in delegate_list:
            missed_vote = d[2] + 1
            x = await db.miss_vote(d[0], missed_vote)
            if missed_vote >= 3:
                await db.deactivate_delegate(d[0])
        return

@bot.tree.command(name="citizen_role", description="set the citizen role for a group")
@app_commands.checks.has_permissions(administrator=True)
async def citizenrole(interaction: discord.Interaction, name: str, role: discord.Role):
    guild_list = await db.get_guilds()
    UNB = await bot.fetch_guild(1260736434193567745)
    for g in guild_list:
        guild_name = UNB.get_role(g[0]).name
        if guild_name.lower() == name.lower() and g[2] == interaction.guild_id:
            await db.set_guild_citizen(role.id)
            await interaction.response.send_message(f"You've set the role id for {guild_name} to {role.name}", ephemeral=True)
            return
    await interaction.response.send_message("Sorry, something went wrong with the command. Please make sure the guild name you type in is correct. You can check by running /guild_check in the UNB server.")
    return

@bot.tree.command(name="set_server", description="set a discord server for a group")
@app_commands.checks.has_permissions(administrator=True)
async def setserver(interaction: discord.Interaction, name: str):
    guild_list = await db.get_guilds()
    UNB = await bot.fetch_guild(1260736434193567745)
    for g in guild_list:
        guild_name = UNB.get_role(g[0]).name
        if guild_name.lower() == name.lower():
            await db.set_guild_server(interaction.guild_id)
            await interaction.response.send_message(f"You have change the server id for {guild_name} to {interaction.guild_id}", ephemeral = True)
            return
    await interaction.response.send_message("Sorry, something went wrong with the command. Please make sure the guild name you type in is correct. You can check by running /guild_check in the UNB server.")
    return

@bot.tree.command(name="extend_vote",description = "Vote to extend the current vote's discussion or vote time.", guild=GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def extend_vote(interaction: discord.Interaction, proposal_id: int):
    check = await db.get_proposal(proposal_id)
    if check == None:
        await interaction.response.send_message("It doesn't look like there's a proposal with that id.", ephemeral = True)
    if bool(check[3]):
        await interaction.response.send_message("This vote is completed already.", ephemeral = True)
    data = await db.extend_vote(proposal_id)
    await interaction.response.send_message(f"You have voted to extend time on proposal {proposal_id}.", ephemeral = True)
    if data[1] == 4:
        time = datetime.datetime.fromtimestamp(data[2]) + datetime.timedelta(hours=48)
        time = time.timestamp()
        await db.extend_time(proposal_id, time)
        await GENERAL_ASSEMBLY.send(f"""
        <@&1348752329964388383>
        Enough Delegates have voted to extend the {"voting" if data[3] else "discussion"} time for proposal {proposal_id}.
        The new end time for {"voting" if data[3] else "discussion"} is <t:{int(time)}:F> which is <t:{int(time)}:R>.
        The time cannot be extended past this point.
        """)
    return

@bot.tree.command(name="populate", description = "populate db with guilds", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def populate(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    guild_list = await db.get_guilds()
    delegate_list = await db.get_all_delegates()
    for g in guild_list:
        count = 0
        for d in delegate_list:
                if d[1] == g[0]:
                    count += 1
        for d in delegate_list:
            if d[1] == g[0]:
                await db.set_power(d[0], float(g[3])/float(count))
    await interaction.followup.send("Hey it's done")

@bot.command()
async def synccmd(ctx: commands.Context):
    fmt = await bot.tree.sync(guild = GUILD_ID)
    await ctx.send(
        f"Synced {len(fmt)} commands to the current server",
        delete_after = 1.0
    )
    await ctx.message.delete()
    return

@bot.command()
async def globalsync(ctx: commands.Context):
    fmt = await bot.tree.sync()
    await ctx.send(
        f"Synced {len(fmt)} commands globally. This might take a while.",
        delete_after = 1.0
    )
    await ctx.message.delete()
    return

@tasks.loop(time=census_time)
async def census_loop():
    if (datetime.datetime.now().weekday() != 0 and datetime.datetime.now().weekday() != 4):
        return
    channel = bot.get_channel(1368195086952960031)
    UNB = await bot.fetch_guild(1260736434193567745)
    output = "```"
    output += f"\nGroup Name {" " * 20} Member Count {" " * 5} Percentage {" " * 5} Change {" " * 5}"
    output += f"\n{"-" * 75}"
    total = 0
    old_total = 0

    guild_list = await db.get_guilds()
    delegate_list = await db.get_delegates()
    for g in guild_list:
        old_total += g[3]
    for g in guild_list:
        if g[2] == 0:
            output += f"\n{UNB.get_role(g[0]).name: <31} {population: <18} {(float(population)/float(old_total)) * 100.0:5.2f} {"5":<10} (0)"
        else:
            server = await bot.fetch_guild(g[2])
            role = await server.fetch_role(g[1])
            population = len(role.members)
            difference = population - g[3]
            total += population
            await db.set_members(g[0], population)
            count = 0
            for d in delegate_list:
                if d[1] == g[0]:
                    count += 1
            for d in delegate_list:
                if d[1] == g[0]:
                    await db.set_power(d[0], float(g[3])/float(count))
            output += f"""
            \n{UNB.get_role(g[0]).name: <31} {population: <18} {(float(population)/float(old_total)) * 100.0:5.2f} {"5":<10} ({difference})"""
    output += f"\n\nThere are currently {total} players represented by the United Nations of Bitcraft.```"
    await channel.send(output)

@tasks.loop(seconds=30)
async def handle_proposal():
    await asyncio.sleep(30)
    global GENERAL_ASSEMBLY
    GENERAL_ASSEMBLY = bot.get_guild(1260736434193567745).get_channel(1348751860030246963)
    await asyncio.sleep(5)
    data = await db.get_timestamps()
    if data == []:
        return
    proposal_id = data[0][0]
    time = data[0][1]
    discussed = bool(data[0][2])
    if datetime.datetime.now().timestamp() >= time:
        if not discussed:
            p = await db.get_proposal(proposal_id)
            new_time = datetime.datetime.now() + datetime.timedelta(hours=36)
            await GENERAL_ASSEMBLY.send(f"""
            <@&1348752329964388383>
            The discussion period for {p[1]} - {p[0]} has ended!
            Voting has now opened for this proposal.
            You can vote using the /vote command, the proposal id is: {p[0]}
            Voting ends <t:{int(new_time.timestamp())}:R> on <t:{int(new_time.timestamp())}:F>.
            """)
            await db.finish_discuss(proposal_id, int(new_time.timestamp()))

        if discussed:
            p = await db.get_proposal(proposal_id)
            await GENERAL_ASSEMBLY.send(f"""
            <@&1348752329964388383>
            The voting has ended for {p[1]} - {p[0]}!
            A UN Admin will run the Tally command shortly to review the results!
            """)
            await db.complete_vote(proposal_id)
    else:
        return

async def check_delegates():
    return

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message("Sorry, you don't have the permissions to run that command.", ephemeral=True)
        return
    if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("Sorry, you don't have the right role to run that command", ephemeral=True)
        return
    if isinstance(error, discord.errors.Forbidden):
        print("Forbidden error. Probably a failed DM.")
        return
    await interaction.response.send_message(f"The bot has thrown the following error: {error}. Please contact Lanidae and send a screenshot of this message.", ephemeral=True)

bot.run(TOKEN)