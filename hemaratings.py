import os
import requests
import discord
from dotenv import load_dotenv
from discord import app_commands
from bs4 import BeautifulSoup
from thefuzz import fuzz

load_dotenv()

intents = discord.Intents.default()
client = discord.Client(intents=intents, activity=discord.Game(name='hemaratings.com'))
tree = app_commands.CommandTree(client)
fencers = []

# Load fencers on startup
@client.event
async def on_ready():
    print('Loading fencers...')
    get_fencers() # Load fencers
    print('Fencers loaded with ' + str(len(fencers)) + ' entries')
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    await tree.sync()

# Display hemaratings by name
@tree.command(name = "hemaratings", description = "Display hemaratings by name")   
async def hemaratings(ctx, name: str):
    fencer = find_fencer(name) # Find fencer by name
    if fencer:
        await ctx.response.send_message(embed=get_fencer_info(fencer))
    else:
        await ctx.response.send_message("Fencer " + name + " not found", delete_after=10, ephemeral=True)

# Find fencer by name
def find_fencer(name):
    for fencer in fencers:
        score = fuzz.token_sort_ratio(fencer["text"], name) # Calculate similarity score
        if score > 80:
            return fencer 
    return False

# Get fencer info from hemaratings.com
def get_fencer_info(fencer):    
    url = "https://hemaratings.com" + fencer["href"]
    response = requests.get(url) # Get the page
    soup = BeautifulSoup(response.content, "html.parser") # Parse the page
    
    details = soup.find_all("article")[0]
    flag = details.find("i", {"class": "flag-icon"}).get("class")[1].split("-")[2]
    group = details.find("a").text

    # Create embed
    if group:
        embed=discord.Embed(title=fencer['text'], url="https://hemaratings.com" + fencer["href"], description="Data from hemaratings about " + fencer['text'] + " from " + group, color=0x109319) 
    else:
        embed=discord.Embed(title=fencer['text'], url="https://hemaratings.com" + fencer["href"], description="Data from hemaratings about " + fencer['text'], color=0x109319)       

    if flag:
        embed.set_thumbnail(url="https://flagsapi.com/" + flag.upper() + "/flat/64.png")

    ratings = soup.find_all("article")[2]
    table = ratings.find("table")
    body = table.find("tbody")
    rows = body.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        embed.add_field(name=cells[0].text, value=cells[1].text + " (" + cells[2].text + ") ", inline=True)   

    return embed

# Get all fencers from hemaratings.com
def get_fencers():
    url = "https://hemaratings.com/fighters/"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", {"id": "mainTable"}) # find the table by its ID
    rows = table.find_all("tr") # find all rows in the table

    for row in rows:
        cells = row.find_all("td") # find all cells in the row
        if len(cells) > 0: # check if there are any cells in the row
            first_cell = cells[0] # select the first cell in the row
            anchor = first_cell.find("a") # find the anchor tag in the cell
            if anchor is not None: # check if an anchor tag was found
                fencers.append({
                "href": anchor.get("href"),
                "text": anchor.text
            })

client.run(os.getenv("DISCORD_API_KEY"))