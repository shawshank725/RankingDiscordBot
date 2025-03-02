import discord, os,sqlite3
from discord.ext import commands
from discord import app_commands
from read_env import *
from sql_queries import *
import math, re

#intent settings
intents = discord.Intents.default()
intents.members = True  # Enable members intent
intents.message_content = True  # Enable message content intent
message_min_length = 4
server_emojis = []

#loading token and bot
bot = commands.Bot(command_prefix='/', intents=intents)
load_env_file(".env")
TOKEN = os.getenv("TOKEN")

#sql connection and cursor
connection = sqlite3.connect("server_data.db")
cursor_obj = connection.cursor()
cursor_obj.execute(query_to_create_table)

### emoji pattern
UNICODE_EMOJI_PATTERN = re.compile(
    "[\U0001F600-\U0001F64F]|"  # Emoticons
    "[\U0001F300-\U0001F5FF]|"  # Misc Symbols and Pictographs
    "[\U0001F680-\U0001F6FF]|"  # Transport and Map Symbols
    "[\U0001F700-\U0001F77F]|"  # Alchemical Symbols
    "[\U0001F780-\U0001F7FF]|"  # Geometric Shapes Extended
    "[\U0001F800-\U0001F8FF]|"  # Supplemental Arrows-C
    "[\U0001F900-\U0001F9FF]|"  # Supplemental Symbols and Pictographs
    "[\U0001FA00-\U0001FA6F]|"  # Chess Symbols
    "[\U0001FA70-\U0001FAFF]|"  # Symbols and Pictographs Extended-A
    "[\U00002700-\U000027BF]|"  # Dingbats
    "[\U000024C2-\U0001F251]"   # Enclosed characters
)
DISCORD_EMOJI_PATTERN = re.compile(r"<a?:\w+:\d+>")

def contains_unicode_emoji(message):
    return bool(UNICODE_EMOJI_PATTERN.search(message))

def contains_custom_emoji(message):
    return bool(DISCORD_EMOJI_PATTERN.search(message))

def contains_emoji(message):
    return contains_unicode_emoji(message) or contains_custom_emoji(message)

@bot.event
async def on_ready():  # Called when bot is ready
    await bot.change_presence(status=discord.Status.online,
                                 activity=discord.Activity(type=discord.ActivityType.listening, name="'en' prefix!"))     
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands(s)")
    except Exception as e:
        print(e)
    print(f"We have logged in as {bot.user}")


####### RANKING CODE
@bot.event
async def on_member_join(member):
    # Send a welcome message in a specific channel
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if channel:
        await channel.send(f"Welcome to the server, {member.mention}! 🎉")

    # Add the "Beginner" role to the new member
    role = discord.utils.get(member.guild.roles, name="Beginner")
    if role:
        await member.add_roles(role)
        try:
            cursor_obj.execute(query_to_insert,(str(member.id), member.name,))
            connection.commit()
        except Exception as e:
            print(f"Couldnt add {member.name} to database." + e)
      
@bot.event
async def on_message(message):
    user_who_messaged = message.author
    user_who_messaged_id = str(user_who_messaged.id)
    
    if user_who_messaged == bot.user:
        return

    if message.type == discord.MessageType.new_member:
        return
    
    try: 
        cursor_obj.execute(query_to_get_user_info, (user_who_messaged_id,))
        result = cursor_obj.fetchone()  # Fetch a single row (level, xp)
        user_level, user_xp = result
        if not ((len(message.content) < message_min_length) or contains_emoji(message.content)):
            user_xp = math.ceil(user_xp + user_xp/user_level*0.001*len(message.content)/4)

        if user_xp >=100:
            user_xp = user_xp -100 + 1
            user_level = user_level + 1
            await message.channel.send(f"Congratulations {user_who_messaged.mention}. You just advanced to level {user_level}!")

        ########assigning the user roles based on level#####
        if user_level >10:
            role = discord.utils.get(message.guild.roles, name="Intermediate")
            if role:
                await user_who_messaged.add_roles(role)
                
        if user_level >20:
            role = discord.utils.get(message.guild.roles, name="Advanced")
            if role:
                await user_who_messaged.add_roles(role)

        if user_level >30:
            role = discord.utils.get(message.guild.roles, name="Expert")
            if role:
                await user_who_messaged.add_roles(role)
                
        if user_level >40:
            role = discord.utils.get(message.guild.roles, name="Master")
            if role:
                await user_who_messaged.add_roles(role)
 
        cursor_obj.execute(query_to_update, (user_xp, user_level, user_who_messaged_id,))
        connection.commit()
    except Exception as e:
        print(e)

@bot.tree.command(name="rank", description="Displays your rank in the server")
async def rank(interaction: discord.Interaction, member: discord.Member = None):
    guild = interaction.guild
    if not guild:  # Ensure the command is used in a server
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    member_to_check = member or interaction.user
    if member_to_check.bot:
        await interaction.response.send_message("You cannot check the rank of a bot!", ephemeral=True)
        return
    
    user_who_used_slash = member_to_check.id
    embed = discord.Embed(colour=discord.Colour.green())
    list_of_users = cursor_obj.execute(query_to_get_users_desc)
    rank = 1
    req_level = 0
    req_xp = 0
    for i in list_of_users:
        if i[0] == str(user_who_used_slash):
            req_level = i[2]
            req_xp = i[3]
            break
        else:
            rank = rank +1

    no_of_green_squares = (req_xp // 10)
    no_of_white_squares = 10 - no_of_green_squares

    green_square = ":green_square:"
    white_square = ":white_large_square:"
    progress_bar = (green_square * no_of_green_squares) + (white_square * no_of_white_squares)
    
    embed.set_thumbnail(url = member_to_check.avatar.url)
    embed.add_field(name=f"Rank - #{rank} \nUser: {member_to_check.name}", value="", inline = False )
    embed.add_field(name=f"Level: {req_level} \nXP: {req_xp}% \n{progress_bar}", value="", inline = False )
    
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="top3", description="Displays top 3 chatters in the server")
async def top3(interaction: discord.Interaction):
    guild = interaction.guild
    if not guild:  # Ensure the command is used in a server
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    list_of_users = cursor_obj.execute(query_to_get_users_desc).fetchmany(3)

    embeds = []
    for i, user_data in enumerate(list_of_users):
        user_id, username, req_level, req_xp = user_data  # Unpack the user data
        rank = i + 1
        no_of_green_squares = req_xp // 10
        no_of_white_squares = 10 - no_of_green_squares

        green_square = ":green_square:"
        white_square = ":white_large_square:"
        progress_bar = (green_square * no_of_green_squares) + (white_square * no_of_white_squares)

        # Get the member object to retrieve display name or fallback to the username
        member = guild.get_member(int(user_id))
        display_name = member.display_name if member else username
        
        embed = discord.Embed(colour=discord.Colour.green())
        embed.set_thumbnail(url = member.avatar.url)
        embed.add_field(
            name=f"Rank #{rank}: {display_name}",
            value=f"Level: {req_level}\nXP: {req_xp}%\n{progress_bar}",
            inline=False
        )
        embeds.append(embed)
        
    await interaction.response.send_message(embeds=embeds)




##### DATA MANIPULATION COMMANDS

# Define the command
@bot.tree.command(name="reset_db",description="Can be used ONLY by server owner!")
async def reset_db(interaction: discord.Interaction):
    if interaction.user.id == interaction.guild.owner_id:
        cursor_obj.execute(query_to_reset)
        connection.commit()
        await interaction.response.send_message("Database reset done!",ephemeral = True)
    else:
        await interaction.response.send_message("You are not the server owner. This command is restricted.",ephemeral = True)


@bot.tree.command(name="adddata", description="Adds user data. Can be used only by server owner!")
async def adddata(interaction: discord.Interaction, user_id:int):
    user = await bot.fetch_user(user_id)
    if interaction.user.id == interaction.guild.owner_id:
        cursor_obj.execute(query_to_insert,(user_id,user))
        connection.commit()
        await interaction.response.send_message("Data of user {} added!".format(user),ephemeral = True)
    else:
        await interaction.response.send_message("You are not the server owner. This command is restricted.",ephemeral = True)





###### MISC COMMANDS

@bot.tree.command(name="hello", description="Says hello!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello! How are you today, {interaction.user.mention}?")


@bot.tree.command(name="test", description="Test something")
async def test(interaction: discord.Interaction, arg:str):  # Command with argument
    await interaction.response.send_message(arg)


@bot.tree.command(name="evaluate", description="Write any mathematical expression inside quotation marks ")
async def evaluate(interaction: discord.Interaction, arg:str):  # Command without argument
    await interaction.response.send_message(f"Answer to your problem ({arg}) is - {eval(arg)}")


@bot.tree.command(name="people", description="Get list of people in the server")
async def people(interaction: discord.Interaction):
    members = interaction.guild.members  # List of all members in the server
    member_nickname = []
    for i, member in enumerate(members, start=1):
        member_nickname.append(f"{i}. {member.display_name} {member.mention}\n")
    
    # If the member list is too long, truncate to avoid Discord's message length limit
    member_list = ''.join(member_nickname)
    if len(member_list) > 2000:  # Discord message limit
        member_list = member_list[:1997] + "..."
    await interaction.response.send_message(f"Members in this server:\n{member_list}")


@bot.tree.command(name="describe", description="Get bot's description")
async def describe(interaction: discord.Interaction):
    await interaction.response.send_message("Hello there! I'm this server's Bot that can solve any simple mathemtical expression, provide details about this server. I also keep track of ranks and roles, too!")


@bot.tree.command(name="bothelp", description="Get bot's commands list")
async def bothelp(interaction: discord.Interaction):
    message = """This is a list of all commands that I have:
1. /hello - Say hello to me
2. /test - Bot displays your message
3. /evaluate - Evaluate any mathematical expression
4. /describe - Describes the capabilities of the bot
5. /serverinfo - Gives info about the server
6. /people - List all members in this server
7. /rank - Get your or someone's rank
8. /top3 - Get top3 discord chatters """
    await interaction.response.send_message(message)


@bot.tree.command(name="serverinfo", description="Displays information about the server")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    if not guild:  # Ensure the command is used in a server
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return

    total_text_channels = len(guild.text_channels)
    total_voice_channels = len(guild.voice_channels)
    total_members = guild.member_count
    total_channels = total_text_channels + total_voice_channels

    embed = discord.Embed(
        title="Server Info",
        colour=discord.Colour.orange(),
        description="Here is the Server Info",
    )
    embed.add_field(value=f"Total Server Channels: {total_channels}", name="", inline = False )
    embed.add_field(value=f"Total Text Channels: {total_text_channels}", name="" , inline = False)
    embed.add_field(value=f"Total Voice Channels: {total_voice_channels}", name="" , inline = False)
    embed.add_field(value=f"Server Member Count: {total_members}", name="" , inline = False)
    
    await interaction.response.send_message(embed=embed)

bot.run(TOKEN)
