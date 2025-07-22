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

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix = '%', intents=intents)

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
        if handle_proposal.current_loop == 0 and not handle_proposal.is_running():
            handle_proposal.start()

try:
    guilds = pickle.load(open("guilds.p", "rb"))
except FileNotFoundError:
    guilds = []

with open('config.json', 'r') as f:
    config = json.load(f)
    TOKEN = config['token']

GENERAL_ASSEMBLY = None

@bot.event
async def on_ready():
    global GENERAL_ASSEMBLY
    print("UNBot is Running!")
    census_loop.start()
    GENERAL_ASSEMBLY = bot.get_guild(1260736434193567745).get_channel(1348751860030246963)
    handle_proposal.cancel()

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
            g.name = role.name
            await interaction.response.send_message(g.SetCount(count) + " - " + g.SetDelegates(count2), ephemeral = True)
            pickle.dump(guilds, open("guilds.p", "wb"))
            print(f"{interaction.user.name} edited {interaction.guild.get_role(role.id).name} to {count} population - {count2} delegates.")
            return
    temp = VotingGuild(interaction.guild.get_role(role.id).name, role.id, count, count2)
    guilds.append(temp)
    await interaction.response.send_message(temp.SetCount(count) + " - " + temp.SetDelegates(count2), ephemeral = True)
    pickle.dump(guilds, open("guilds.p", "wb"))

@bot.tree.command(name="guild_check", description = "Check all guild data", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def guildcheck(interaction: discord.Interaction):
    output = "```\n"
    total = 0
    del_total = 0
    for g in guilds:
        total += g.Count()
        del_total += g.Delegates()
        print(f"{g.name} - {g.serverid}")
    for g in guilds:
        for r in interaction.guild.roles:
            if r.id == g.Role():
                name = r.name
        output += f"{name:<20} - Members: {g.Count():<5} ({(g.Count()/total)*100:.2f}%){" - Delegates: ":>15}{g.Delegates():<5} ({(g.Delegates()/del_total)*100:.2f}%)\n"
    output += "```"
    await interaction.response.send_message(output, ephemeral=True)

@bot.tree.command(name="guild_count", description = "See the # of members for each guild", guild = GUILD_ID)
@app_commands.checks.has_role(1348752459287367730)
async def guildcount(interaction: discord.Interaction, role: discord.Role):
    for g in guilds:
        if g.Role() == role.id:
            await interaction.response.send_message(f"The guild {interaction.guild.get_role(role.id).name} has `{g.Count()}` members.", ephemeral=True)

@bot.tree.command(name="create_vote", description = "Create a vote", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def createvote(interaction: discord.Interaction, name: str, text: str):
    ts = datetime.datetime.now()
    discuss_time = (ts + datetime.timedelta(hours=48))
    vote_time = (discuss_time + datetime.timedelta(hours=36))
    data = await db.add_proposal(name, text, discuss_time.timestamp(), vote_time.timestamp())
    await interaction.response.send_message(f"""
    {name} - ({data})
    {text}
    Discussion Time Ends <t:{int(discuss_time.timestamp())}:R> on <t:{int(discuss_time.timestamp())}:F>
    """)

@bot.tree.command(name="vote", description="cast your vote", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def vote(interaction:discord.Interaction, proposal_id: int, choice: Responses):
    data = await db.get_proposal(proposal_id)
    if data[3] == 1:
        await interaction.response.send_message("This vote is no longer active and cannot be voted on", ephemeral = True)
        return
    if choice is Responses.yay:
        await db.add_vote(proposal_id, interaction.user.id, choice.value)
        await interaction.response.send_message("Your yes vote has been recorded.", ephemeral = True)
        print(f"{interaction.user.display_name} voted yay.")
        return
    if choice is Responses.nay:
        await db.add_vote(proposal_id, interaction.user.id, choice.value)
        await interaction.response.send_message("Your no vote has been recorded.", ephemeral = True)
        print(f"{interaction.user.display_name} voted nay.")
        return
    if choice is Responses.abstain:
        await db.add_vote(proposal_id, interaction.user.id, choice.value)
        await interaction.response.send_message("Your abstain vote has been recorded.", ephemeral = True)
        print(f"{interaction.user.display_name} voted abs.")
        return
    await interaction.response.send_message("Sorry, it doesn't look like there's a vote with that name. Please try again.", ephemeral = True)
    return

@bot.tree.command(name="listvotes", description="list active votes", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def list_votes(interaction:discord.Interaction):
    data = await db.get_active_proposals()
    output = "```"
    for d in data:
        if len(d[0]) > 20:
            name = d[0][:18] + "..."
        else:
            name = d[0]
        output += f"{name:20} - {d[1]:4}\n"
    await interaction.response.send_message(output)

@bot.tree.command(name="tally", description = "tally a vote", guild = GUILD_ID)
@app_commands.checks.has_role(1348752329964388383)
async def tally(interaction: discord.Interaction, id: int):
    await interaction.response.defer(ephemeral=True)
    yay_total_power = 0.0
    yay_total = 0
    nay_total_power = 0.0
    nay_total = 0
    abs_total_power = 0.0
    abs_total = 0
    total = 0

    # Loop Through Guilds
    for g in guilds:
        # Add to total Delegate and Population Vote
        # For % and quorum calculations
        total += g.Delegates()

    # Loop through all votes for this Proposal
    data = await db.get_votes(id)
    for d in data:
        # Skip if vote is set to default value
        if d[2] == -2:
            continue

        # Initialize Output Strings
        yay_output = "```\nYays: \n"
        nay_output = "```\nNays: \n"
        abs_output = "```\nAbstain: \n"


        # Yay vote processing
        if d[2] == 1:

            #Get user object for role detection
            user = interaction.guild.get_member(d[1])

            #role detection
            for g in guilds:
                for r in interaction.guild.roles:
                    if r in user.roles and r.id == g.Role():
                        # Add Delegate and Population vote to Yay totals
                        yay_total += 1
                        yay_total_power += (float(g.Count())/float(g.Delegates()))

                        # Adding to output string
                        yay_output += f"{user.display_name:<20} - 1 - {(float(g.Count())/float(g.Delegates())):.2f}\n"

        # Nay vote Processing
        if d[2] == -1:

            #Get user object for role detection
            user = interaction.guild.get_member(d[1])

            #role detection
            for g in guilds:
                for r in interaction.guild.roles:
                    if r in user.roles and r.id == g.Role():
                        # Add Delegate and Population vote to Nay totals
                        nay_total += 1
                        nay_total_power += (float(g.Count())/float(g.Delegates()))

                        # Adding to output string
                        nay_output += f"{user.display_name:<20} - 1 - {(float(g.Count())/float(g.Delegates())):.2f}\n"

        # Abstain vote Processing
        if d[2] == 0:

            #Get user object for role detection
            user = interaction.guild.get_member(d[1])

            #role detection
            for g in guilds:
                for r in interaction.guild.roles:
                    if r in user.roles and r.id == g.Role():
                        # Add Delegate and Population vote to Abstain totals
                        abs_total += 1
                        abs_total_power += (float(g.Count())/float(g.Delegates()))

                        # Adding to output string
                        abs_output += f"{user.display_name:<20} - 1 - {(float(g.Count())/float(g.Delegates())):.2f}\n"

    if True: #float((abs_total + nay_total + yay_total)) >= (0.5 * total):
        present_total = yay_total + abs_total + nay_total
        present_total_power = yay_total_power + abs_total_power + nay_total_power
        await interaction.followup.send("There are enough participating delegates, the vote is valid.")
        yay_output += f"\nDelegate Vote: {yay_total}/{present_total} ({float((yay_total)/float(present_total))*100.0:.2f}%)\n"
        yay_output += f"Population Vote: {yay_total_power/present_total_power:.2f} ({(yay_total_power/present_total_power)*100.0:.2f}%)\n```"
        nay_output += f"\nDelegate Vote: {nay_total}/{present_total} ({float((nay_total)/float(present_total))*100.0:.2f}%)\n"
        nay_output += f"Population Vote: {nay_total_power/present_total_power:.2f} ({(nay_total_power/present_total_power)*100.0:.2f}%)\n```"
        abs_output += f"\nDelegate Vote: {abs_total}/{present_total} ({float((abs_total)/float(present_total))*100.0:.2f}%)\n"
        abs_output += f"Population Vote: {abs_total_power/present_total_power:.2f} ({(abs_total_power/present_total_power)*100.0:.2f}%)\n```"
        await interaction.followup.send(yay_output)
        await interaction.followup.send(nay_output)
        await interaction.followup.send(abs_output)
        await db.complete_vote(id)
    else:
        await interaction.followup.send("There aren't enough participating delegates, this is an invalid vote.", ephemeral=True)
        await db.complete_vote(id)
        return

@bot.tree.command(name="census", description="take a census of member groups", guild =  GUILD_ID)
@app_commands.checks.has_role(1348752459287367730)
async def census(interaction: discord.Interaction):
    channel = bot.get_channel(1368195086952960031)
    output = ""
    total = 0
    for g in guilds:
        print(g.name)
        if g.Server() == 0:
            output += f"{g.Name()} member count is {g.Count()}\n"
            total += g.Count()
            continue
        for s in bot.guilds:
            if s.id == g.Server():
                for r in s.roles:
                    if r.id == g.CitizenRole():
                        temp = g.Count()
                        g.SetCount(len(r.members))
                        dif = g.Count() - temp
                        total += g.Count()
                        if dif > 0:
                            output += f"{g.Name()} member count is {len(r.members)} (+{dif})\n"
                            continue
                        elif dif < 0:
                            output += f"{g.Name()} member count is {len(r.members)} ({dif})\n"
                            continue
                        else:
                            output += f"{g.Name()} member count is {len(r.members)}\n"
                            continue

    output += f"There are currently {total} players represented by the United Nations of Bitcraft."
    pickle.dump(guilds, open("guilds.p", "wb"))
    await channel.send(output)
    await interaction.response.send_message("Manual census complete", ephemeral=True)
    print("Census complete")

@bot.tree.command(name="citizen_role", description="set the citizen role for a group")
@app_commands.checks.has_permissions(administrator=True)
async def citizenrole(interaction: discord.Interaction, name: str, role: discord.Role):
    for g in guilds:
        if g.Name().lower() == name.lower() and g.Server() == interaction.guild_id:
            g.SetCitizen(role.id)
            await interaction.response.send_message(f"You've set the role id for {g.Name()} to {g.CitizenRole()}", ephemeral=True)
            pickle.dump(guilds, open("guilds.p", "wb"))
            print(f"Citizen role updated for {g.Name()}")
            return
    await interaction.response.send_message("Sorry, something went wrong with the command. Please make sure the guild name you type in is correct. You can check by running /guild_check in the UNB server.")
    return

@bot.tree.command(name="set_server", description="set a discord server for a group")
@app_commands.checks.has_permissions(administrator=True)
async def setserver(interaction: discord.Interaction, name: str):
    for g in guilds:
        print(f"{g.Name().lower()} - {name}")
        if g.Name().lower() == name.lower():
            g.SetServer(interaction.guild_id)
            pickle.dump(guilds, open("guilds.p", "wb"))
            await interaction.response.send_message(f"You have change the server id for {g.Name()} to {g.Server()}", ephemeral = True)
            print(f"Server id updated for {g.Name()}")
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
    output = ""
    total = 0
    new_total = 0
    for v in guilds:
        total += v.Count()
    for v in guilds:
        if v.Server() == 0:
            output += f"{v.Name()} member count is {v.Count()} - ({(float(v.Count())/float(total))* 100.0:.2f}%)\n"
            continue
        for g in bot.guilds:
            if g.id == v.Server():
                for r in g.roles:
                    if r.id == v.CitizenRole():
                        temp = v.Count()
                        v.SetCount(len(r.members))
                        new_total += len(r.members)
                        dif = v.Count() - temp
                        if dif > 0:
                            output += f"{v.Name()} member count is {len(r.members)} - ({(float(len(r.members))/float(total))* 100.0:.2f}%) (+{dif})\n"
                            continue
                        elif dif < 0:
                            output += f"{v.Name()} member count is {len(r.members)} - ({(float(len(r.members))/float(total))* 100.0:.2f}%) ({dif})\n"
                            continue
                        else:
                            output += f"{v.Name()} member count is {len(r.members)} - ({(float(len(r.members))/float(total))* 100.0:.2f}%)\n"
                            continue

    output += f"There are currently {new_total} players represented by the United Nations of Bitcraft."
    pickle.dump(guilds, open("guilds.p", "wb"))
    await channel.send(output)
    print("Auto census complete")

@tasks.loop(seconds=30)
async def handle_proposal():
    data = await db.get_timestamps()
    if data == None:
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