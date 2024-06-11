import os
import discord
from discord.ext import commands
import json

intents = discord.Intents.default()
intents.messages = True  # Set the messages intent to True

bot = commands.Bot(command_prefix='!', intents=intents)

# Define the IDs of the admin roles
ADMIN_ROLE_IDS = [696594546489819136, 710276581657935902]

# Dictionary to store member IDs and their corresponding names
member_names = {
    737408742865371136: "Cbuck",
    613474031995322369: "Bren",
    196086626605203456: "Doove",
    393616924677898240: "Kirdy123",
    689348945293738007: "L/cas",
    508460797027024933: "Shaboob",
    419341004135464976: "Spidaman",
    554563448919556116: "Fronk",
    210522910408966144: "Michael"
}

# Load counts from a JSON file on bot startup
def load_counts():
    try:
        with open("drink_counts.json", "r") as file:
            data = json.load(file)
            print("Loaded drink counts:", data)  # Debug information
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading counts: {e}")  # Debug information
        data = {
            'beer': {},
            'wine': {},
            'mixeddrink': {},
            'shot': {}
        }
    return data

# Save counts to a JSON file
def save_counts():
    with open("drink_counts.json", "w") as file:
        json.dump(drink_counts, file)
    print("Saved drink counts:", drink_counts)  # Debug information

# Call load_counts() on bot startup
drink_counts = load_counts()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    print("Current drink counts on ready:", drink_counts)  # Debug information

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command(name='hello', help='Responds with Hello!')
async def hello(ctx):
    await ctx.send('Hello!')
    save_counts()

# Function to increment drink count
async def increment_drink(ctx, drink_type: str):
    update_count(ctx.author.id, drink_type)
    await ctx.send(f'{drink_type.capitalize()} count incremented for {ctx.author.name}')
    await display_counts(ctx)
    save_counts()

# Command to increment beer count
@bot.command(name='beer', help='Increment beer count')
async def beer(ctx):
    await increment_drink(ctx, 'beer')

# Command to increment wine count
@bot.command(name='wine', help='Increment wine count')
async def wine(ctx):
    await increment_drink(ctx, 'wine')

# Command to increment mixed drink count
@bot.command(name='mixeddrink', help='Increment mixed drink count')
async def mixeddrink(ctx):
    await increment_drink(ctx, 'mixeddrink')

# Command to increment shot count
@bot.command(name='shot', help='Increment shot count')
async def shot(ctx):
    await increment_drink(ctx, 'shot')

# Command to display drink leaderboard
@bot.command(name='leaderboard', help='Show drink leaderboard')
async def leaderboard(ctx):
    total_drinks = 0
    leaderboard = []
    for member_id, member_name in member_names.items():
        print(f'Processing {member_name} with ID {member_id}')  # Debug information
        user_total = sum([drink_counts[drink_type].get(str(member_id), 0) for drink_type in drink_counts])
        print(f'{member_name} total drinks: {user_total}')  # Debug information
        total_drinks += user_total
        leaderboard.append((user_total, member_name))

    leaderboard.sort(reverse=True, key=lambda x: x[0])

    message = f'Total drinks combined: {total_drinks}\n'
    for rank, (user_total, member_name) in enumerate(leaderboard, start=1):
        message += f'{rank}. {member_name} : {user_total}\n'

    print("Leaderboard:", leaderboard)  # Debug information
    await ctx.send('```' + message + '```')
    save_counts()

# Function to check if user is admin
def is_admin(ctx):
    return any(role.id in ADMIN_ROLE_IDS for role in ctx.author.roles)

# Command to reset the overall leaderboard
@bot.command(name='reset_overall', help='Reset the overall leaderboard (admin only)')
async def reset_overall(ctx):
    if not is_admin(ctx):
        await ctx.send("You do not have permission to use this command.")
        return
    for drink in drink_counts:
        drink_counts[drink] = {}
    await ctx.send('Overall leaderboard has been reset.')
    save_counts()

# Command to reset a specific user's drinks
@bot.command(name='reset_user', help='Reset specific user\'s drinks (admin only)')
async def reset_user(ctx, user: discord.Member):
    if not is_admin(ctx):
        await ctx.send("You do not have permission to use this command.")
        return
    for drink in drink_counts:
        if str(user.id) in drink_counts[drink]:
            drink_counts[drink][str(user.id)] = 0
    await ctx.send(f'Drinks for {user.name} have been reset.')
    save_counts()

# Command to reset a specific drink type for a user
@bot.command(name='reset_drink', help='Reset a specific drink type for a user (admin only)')
async def reset_drink(ctx, user: discord.Member, drink_type: str):
    if not is_admin(ctx):
        await ctx.send("You do not have permission to use this command.")
        return
    drink_type = drink_type.lower()
    if drink_type in drink_counts and str(user.id) in drink_counts[drink_type]:
        drink_counts[drink_type][str(user.id)] = 0
        await ctx.send(f'{drink_type.capitalize()} count for {user.name} has been reset.')
    else:
        await ctx.send(f'Invalid drink type or user has no record of that drink.')
    save_counts()

# Command to adjust a specific drink count for a user
@bot.command(name='adjust_drink', help='Adjust a specific drink count for a user (admin only)')
async def adjust_drink(ctx, user: discord.Member, drink_type: str, amount: int):
    if not is_admin(ctx):
        await ctx.send("You do not have permission to use this command.")
        return
    drink_type = drink_type.lower()
    if drink_type in drink_counts:
        if str(user.id) not in drink_counts[drink_type]:
            drink_counts[drink_type][str(user.id)] = 0
        drink_counts[drink_type][str(user.id)] += amount
        await ctx.send(f'{drink_type.capitalize()} count for {user.name} has been adjusted by {amount}.')
    else:
        await ctx.send(f'Invalid drink type.')
    save_counts()

# Function to display drink counts
async def display_counts(ctx):
    user_id = ctx.author.id
    message = f'{ctx.author.name}\n'
    total_drinks = 0

    for drink, counts in drink_counts.items():
        count = counts.get(str(user_id), 0)  # Ensure user_id is treated as a string
        total_drinks += count
        message += f'{drink.capitalize()}: {count}\n'

    message += f'Total Drink Count: {total_drinks}'
    print(f"Displaying counts for {ctx.author.name}: {message}")  # Debug information
    await ctx.send(message)

# Function to update drink count
def update_count(author_id: int, drink: str, amount: int = 1):
    author_id = str(author_id)  # Ensure the author ID is a string
    if author_id not in drink_counts[drink]:
        drink_counts[drink][author_id] = 0
    drink_counts[drink][author_id] += amount
    print(f"Updated counts for {author_id}: {drink_counts[drink]}")  # Debug information

# Ensure counts are loaded and saved correctly
drink_counts = load_counts()

# Bot token handling
token = os.getenv("TOKEN")
if token is None or token == "":
    print("Please add your token to the Secrets pane.")
else:
    try:
        bot.run(token)
    except discord.HTTPException as e:
        if e.status == 429:
            print("The Discord servers denied the connection for making too many requests")
            print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
        else:
            raise e
