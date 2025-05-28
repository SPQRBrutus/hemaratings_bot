"""Module for the hemaratings Discord bot."""
import os
import re
import requests
import discord
from discord.ext import tasks
from discord import app_commands
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from thefuzz import fuzz

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(
    intents=intents, activity=discord.Game(name='hemaratings.com'))
tree = app_commands.CommandTree(client)
fencers = []


@client.event
async def on_ready():
    """Load data and start bot session."""
    reload_fencers.start()
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    for guild in client.guilds:        
        print(f"Connected to {guild.name} with {guild.member_count} members")
    await tree.sync()

# Display hemaratings by name
@tree.command(name="hemaratings", description="Display hemaratings by name")
async def hemaratings(ctx, name: str):
    """Display hemaratings by name command."""
    fencer = find_fencer(name)  # Find fencer by name
    if fencer:
        await ctx.response.send_message(embed=get_fencer_info(fencer))
    else:
        await ctx.response.send_message(
            "Fencer " + name + " not found", 
            delete_after=10,
            ephemeral=True
        )

# Find fencer by name
def find_fencer(name):
    """Find fencer by name using fuzzy search."""

    #Exact match
    for fencer in fencers:
        if fencer["text"].lower() == name.lower():
            return fencer

    for fencer in fencers:
        # Calculate similarity score
        score = fuzz.token_sort_ratio(fencer["text"], name)
        if score > 80:
            return fencer
    return False

# Get fencer info from hemaratings.com
def get_fencer_info(fencer):
    """Get fencer info from hemaratings.com."""
    url = "https://hemaratings.com" + fencer["href"]
    response = requests.get(url, timeout=30)  # Get the page
    soup = BeautifulSoup(response.content, "html.parser")  # Parse the page

    details = soup.find_all("article")[0]
    flag = details.find("i", {"class": "flag-icon"}
                        ).get("class")[1].split("-")[2]
    group = details.find("a").text

    # Create embed
    if group:
        embed = discord.Embed(
            title=fencer['text'],
            url="https://hemaratings.com" + fencer["href"],
            description="Data from hemaratings about " + fencer['text'] + " from " + group,
            color=0x109319
        )
    else:
        embed = discord.Embed(
            title=fencer['text'],
            url="https://hemaratings.com" + fencer["href"],
            description="Data from hemaratings about " + fencer['text'],
            color=0x109319
        )

    if flag:
        embed.set_thumbnail(url="https://flagsapi.com/" +
                            flag.upper() + "/flat/64.png")

    ratings = soup.find_all("article")[1]
    table = ratings.find("table")
    body = table.find("tbody")
    rows = body.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) > 1:
            rating = re.sub(r"\(.*?\)", "", cells[1].text)
            embed.add_field(
                name=cells[0].text.lstrip("- "),
                value=rating + " (" + cells[2].text + ") ".replace("\n", ""),
                inline=True
            )

    return embed

# Get all fencers from hemaratings.com
async def get_fencers():
    """Get all fencers from hemaratings.com."""
    url = "https://hemaratings.com/fighters/"
    response = requests.get(url, timeout=30)

    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", {"id": "mainTable"})  # find the table by its ID
    rows = table.find_all("tr")  # find all rows in the table
    fencers.clear()  # clear the fencers list

    for row in rows:
        cells = row.find_all("td")  # find all cells in the row
        if len(cells) > 0:  # check if there are any cells in the row
            first_cell = cells[0]  # select the first cell in the row
            anchor = first_cell.find("a")  # find the anchor tag in the cell
            if anchor is not None:  # check if an anchor tag was found
                fencers.append({
                    "href": anchor.get("href"),
                    "text": anchor.text
                })

# Reload fencers every 24 hours
@tasks.loop(hours=24)
async def reload_fencers():
    """Reloads the fencers and prints the number of entries loaded."""
    print('Loading fencers...')
    await get_fencers()
    print('Fencers loaded with ' + str(len(fencers)) + ' entries')

client.run(os.getenv("DISCORD_API_KEY"))
