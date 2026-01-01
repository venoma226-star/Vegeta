import os
import uuid
import hashlib
import asyncio
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from flask import Flask
import aiosqlite
from threading import Thread

# ===================== FLASK (RENDER KEEPALIVE) =====================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask).start()

# ===================== DISCORD BOT =====================
intents = discord.Intents.default()
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===================== DATABASE =====================
DB_FILE = "giveaways.db"

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS giveaways (
            id TEXT PRIMARY KEY,
            guild_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            message_id INTEGER,

            header TEXT NOT NULL,
            points TEXT,
            emoji TEXT NOT NULL,

            winner_id INTEGER NOT NULL,
            winners_count INTEGER NOT NULL,

            end_time TEXT NOT NULL,
            status TEXT NOT NULL,

            checksum TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
        await db.commit()

asyncio.run(init_db())

# ===================== HELPERS =====================
def make_checksum(winner_id, guild_id, end_time):
    raw = f"{winner_id}{guild_id}{int(datetime.fromisoformat(end_time).timestamp())}"
    return hashlib.sha256(raw.encode()).hexdigest()

def parse_duration(amount, unit):
    if unit == "s":
        return timedelta(seconds=amount)
    if unit == "m":
        return timedelta(minutes=amount)
    if unit == "h":
        return timedelta(hours=amount)
    if unit == "d":
        return timedelta(days=amount)
    return timedelta(minutes=amount)

def format_points(points):
    return "\n".join(f"• {p}" for p in points)

def get_time_remaining(end_time):
    delta = end_time - datetime.utcnow()
    if delta.total_seconds() <= 0:
        return "0s"
    days, remainder = divmod(delta.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts = []
    if days > 0: parts.append(f"{int(days)}d")
    if hours > 0: parts.append(f"{int(hours)}h")
    if minutes > 0: parts.append(f"{int(minutes)}m")
    parts.append(f"{int(seconds)}s")
    return " ".join(parts)

# ===================== GIVEAWAY COMMAND =====================
@bot.tree.command(name="giveaway", description="Start a giveaway")
@app_commands.describe(
    header="Header text",
    points="Points separated by ;",
    emoji="Entry emoji",
    duration="Giveaway duration (number)",
    unit="Unit: s/m/h/d",
    winner="Forced winner",
    winners_count="Number of winners (default 1)"
)
async def giveaway(interaction: discord.Interaction, header: str, points: str, emoji: str,
                   duration: int, unit: str, winner: discord.Member, winners_count: int = 1):

    await interaction.response.defer(ephemeral=True)
    end_time = datetime.utcnow() + parse_duration(duration, unit)
    points_list = points.split(";")
    giveaway_id = str(uuid.uuid4())
    checksum = make_checksum(winner.id, interaction.guild.id, end_time.isoformat())

    # initial embed
    embed = discord.Embed(title="🎉 " + header, color=discord.Color.green())
    embed.description = f"{format_points(points_list)}\n\n" \
                        f"🏆 Winners: {winners_count}\n" \
                        f"🎭 Entry Emoji: {emoji}\n\n" \
                        f"⏳ Time Remaining: {get_time_remaining(end_time)}\n\n" \
                        f"React with {emoji} to enter!"

    message = await interaction.channel.send(embed=embed)
    await message.add_reaction(emoji)

    # store in DB
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            INSERT INTO giveaways (id, guild_id, channel_id, message_id, header, points, emoji, winner_id, winners_count, end_time, status, checksum, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (giveaway_id, interaction.guild.id, interaction.channel.id, message.id,
              header, ";".join(points_list), emoji, winner.id, winners_count,
              end_time.isoformat(), "active", checksum, datetime.utcnow().isoformat()))
        await db.commit()

    await interaction.followup.send(f"Giveaway created! Winner: {winner.mention}", ephemeral=True)

    # dynamic countdown
    while True:
        remaining = end_time - datetime.utcnow()
        if remaining.total_seconds() <= 0:
            break
        embed.description = f"{format_points(points_list)}\n\n" \
                            f"🏆 Winners: {winners_count}\n" \
                            f"🎭 Entry Emoji: {emoji}\n\n" \
                            f"⏳ Time Remaining: {get_time_remaining(end_time)}\n\n" \
                            f"React with {emoji} to enter!"
        try:
            await message.edit(embed=embed)
        except:
            pass  # message might be deleted
        await asyncio.sleep(30)  # update every 30s

    # finalize giveaway
    async with aiosqlite.connect(DB_FILE) as db:
        async with db.execute("SELECT * FROM giveaways WHERE id = ?", (giveaway_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                return
            # validate checksum
            if make_checksum(row[7], row[1], row[9]) != row[11]:
                await interaction.channel.send("❌ Giveaway cancelled due to data integrity loss.")
                await db.execute("UPDATE giveaways SET status=? WHERE id=?", ("cancelled", giveaway_id))
                await db.commit()
                return
            winner_user = interaction.guild.get_member(row[7])
            await interaction.channel.send(f"🎉 Giveaway ended! Winner: {winner_user.mention}")
            await db.execute("UPDATE giveaways SET status=? WHERE id=?", ("ended", giveaway_id))
            await db.commit()

# ===================== START BOT =====================
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print("Failed to sync commands:", e)
    print(f"Logged in as {bot.user}!")

bot.run(os.environ["DISCORD_TOKEN"])
