import os
import random
import asyncio
import nextcord
from nextcord.ext import commands
from nextcord import Interaction
from flask import Flask
import threading

# ---------------- CONFIG ----------------
TOKEN = os.environ.get("TOKEN")

CHANNEL_ID = 1448181797786750988
AUTHORIZED_USER = 1355140133661184221

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- PERSONALITY MESSAGE POOLS ----------------
personality_messages = {
    "brit_lad": [
        "bruv that’s actually mad",
        "nah man that’s peak",
        "oi allow it fam",
        "man's not dealing w that rn",
        "this whole thing is tapped ngl"
    ],
    "quiet_guy": [
        "idk man feels weird tbh",
        "yeah that’s fine i guess",
        "just chilling tbh",
        "lowkey tired rn",
        "fair enough man"
    ],
    "roadman": [
        "wagwan g",
        "man’s not on that smoke today",
        "you're moving mad bruv",
        "that’s bare long",
        "man's patterned still"
    ],
    "sarcastic_girl": [
        "wow amazing innit 💀",
        "love that for you oml",
        "nah cause that’s crazy",
        "lmao be serious pls",
        "im crying this is too stupid"
    ],
    "emo_kid": [
        "everything’s long tbh",
        "idk nothing feels real",
        "lol whatever man",
        "nah this world’s cooked",
        "bro reality is insane"
    ],
    "normal_teen": [
        "nah that’s jokes 💀",
        "man said wild behaviour",
        "ok but that’s kinda funny",
        "bro what’s even happening",
        "idk but it’s calm"
    ],
    "older_guy": [
        "mate i can’t be bothered today",
        "proper long day ngl",
        "i swear the weather’s moving mad",
        "you lot are wild",
        "honestly unbelievable man"
    ],
    "brit_kid": [
        "innit bruv im hungry",
        "bro i want a snack lowkey",
        "man needs a drink",
        "this is actually jokes",
        "lmao im bored"
    ]
}

# Rare deep messages
deep_messages = [
    "ngl man sometimes life’s just properly confusing",
    "ain’t even gonna lie today’s been long as hell",
    "idk bro feels like everyone’s losing it lately",
    "man just wants a meal deal and peace",
    "bro everything’s moving mad slowly"
]

emojis = ["💀", "😂", "😭", "😮‍💨", "🫡", "🤦‍♂️", "😔", "🔥", "😹"]

farm_running = False

# ---------------- GENERATE HUMAN-LIKE MESSAGE ----------------
async def generate_message(guild):
    # Pick random personality
    personality = random.choice(list(personality_messages.keys()))
    msg = random.choice(personality_messages[personality])

    # 20% chance add emoji
    if random.random() < 0.20:
        msg += " " + random.choice(emojis)

    # 15% chance add extra letters: "bruvvv", "mannn"
    if random.random() < 0.15:
        msg = msg.replace("man", "mannn").replace("bruv", "bruvvv")

    # 10% chance send a deep message
    if random.random() < 0.10:
        msg = random.choice(deep_messages)

    # 12% chance @mention someone
    if random.random() < 0.12:
        members = [m for m in guild.members if not m.bot]
        if members:
            target = random.choice(members)
            msg = f"{target.mention} {msg}"

    return msg


# ---------------- FARM LOOP ----------------
async def farm_loop():
    global farm_running
    channel = bot.get_channel(CHANNEL_ID)
    guild = channel.guild

    while farm_running:
        # Randomly decide multi-message chain
        chain_len = 1
        if random.random() < 0.20:
            chain_len = random.randint(2, 4)

        for _ in range(chain_len):
            if not farm_running:
                break

            msg = await generate_message(guild)
            await channel.send(msg)

            # Small delay between chain messages
            await asyncio.sleep(random.uniform(0.8, 2.2))

        # Rest delay
        delay = random.uniform(2.5, 7.5)

        # 10% chance of long delay (thinking)
        if random.random() < 0.10:
            delay = random.uniform(6, 10)

        # 10% chance of fast reply
        if random.random() < 0.10:
            delay = random.uniform(1, 2)

        await asyncio.sleep(delay)


# ---------------- COMMANDS ----------------
@bot.slash_command(name="startfarm", description="Start ultra natural Pokétwo farming")
async def startfarm(interaction: Interaction):
    global farm_running

    if interaction.user.id != AUTHORIZED_USER:
        await interaction.response.send_message("You're not authorized.", ephemeral=True)
        return

    if farm_running:
        await interaction.response.send_message("Farm already running!", ephemeral=True)
        return

    farm_running = True
    bot.loop.create_task(farm_loop())
    await interaction.response.send_message("🇬🇧 Ultra Natural British Pokétwo Farming Started", ephemeral=True)


@bot.slash_command(name="stopfarm", description="Stop Pokétwo farming")
async def stopfarm(interaction: Interaction):
    global farm_running

    if interaction.user.id != AUTHORIZED_USER:
        await interaction.response.send_message("You're not authorized.", ephemeral=True)
        return

    farm_running = False
    await interaction.response.send_message("Farm stopped.", ephemeral=True)


# ---------------- READY ----------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


# ---------------- FLASK KEEP-ALIVE ----------------
app = Flask("")

@app.route("/")
def home():
    return "Ultra Natural Pokétwo Farm Running 🇬🇧"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ---------------- RUN ----------------
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN)
