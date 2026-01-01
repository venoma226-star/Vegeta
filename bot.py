import os
import uuid
import hashlib
import asyncio
from datetime import datetime, timedelta

import discord
from discord import app_commands
from discord.ext import commands

from flask import Flask
from threading import Thread
import aiosqlite

# ================= FLASK =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Alive"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask, daemon=True).start()

# ================= BOT =================
intents = discord.Intents.default()
intents.reactions = True
bot = commands.Bot(command_prefix="!", intents=intents)

DB_FILE = "giveaways.db"

# ================= DB INIT =================
async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS giveaways (
            id TEXT PRIMARY KEY,
            channel_id INTEGER,
            message_id INTEGER,
            header TEXT,
            points TEXT,
            emoji TEXT,
            winner_id INTEGER,
            winners_count INTEGER,
            end_time TEXT,
            checksum TEXT,
            status TEXT
        )
        """)
        await db.commit()

asyncio.run(init_db())

# ================= HELPERS =================
def checksum(winner_id, end_time):
    raw = f"{winner_id}{end_time}"
    return hashlib.sha256(raw.encode()).hexdigest()

def parse_duration(n, u):
    return {
        "s": timedelta(seconds=n),
        "m": timedelta(minutes=n),
        "h": timedelta(hours=n),
        "d": timedelta(days=n)
    }.get(u, timedelta(minutes=n))

def time_left(end):
    delta = end - datetime.utcnow()
    if delta.total_seconds() <= 0:
        return "0s"
    m, s = divmod(int(delta.total_seconds()), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return f"{d}d {h}h {m}m {s}s"

# ================= BACKGROUND TASK =================
async def run_giveaway(gid):
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute("SELECT * FROM giveaways WHERE id=?", (gid,))
        g = await cur.fetchone()
        if not g:
            return

        channel = bot.get_channel(g[1])
        try:
            message = await channel.fetch_message(g[2])
        except:
            return

        end_time = datetime.fromisoformat(g[8])

        while datetime.utcnow() < end_time:
            embed = message.embeds[0]
            embed.description = embed.description.split("⏳")[0] + \
                f"⏳ Time Remaining: {time_left(end_time)}"
            try:
                await message.edit(embed=embed)
            except:
                pass
            await asyncio.sleep(5)

        # integrity check
        if checksum(g[6], g[8]) != g[9]:
            await channel.send("❌ Giveaway cancelled (data integrity loss).")
            await db.execute("UPDATE giveaways SET status='cancelled' WHERE id=?", (gid,))
            await db.commit()
            return

        winner = await bot.fetch_user(g[6])
        await channel.send(f"🎉 Giveaway Ended! Winner: {winner.mention}")
        await db.execute("UPDATE giveaways SET status='ended' WHERE id=?", (gid,))
        await db.commit()

# ================= SLASH COMMAND =================
@bot.tree.command(name="giveaway", description="Create a forced-winner giveaway")
async def giveaway(
    interaction: discord.Interaction,
    header: str,
    points: str,
    emoji: str,
    duration: int,
    unit: str,
    winner: discord.Member,
    winners_count: int = 1
):
    # ✅ RESPOND IMMEDIATELY
    await interaction.response.send_message(
        "✅ Giveaway created successfully.",
        ephemeral=True
    )

    end = datetime.utcnow() + parse_duration(duration, unit)
    gid = str(uuid.uuid4())

    embed = discord.Embed(title=f"🎉 {header}", color=discord.Color.green())
    embed.description = (
        "\n".join(f"• {p.strip()}" for p in points.split(";")) +
        f"\n\n🏆 Winners: {winners_count}\n"
        f"🎭 Emoji: {emoji}\n\n"
        f"⏳ Time Remaining: {time_left(end)}"
    )

    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction(emoji)

    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        INSERT INTO giveaways VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            gid,
            interaction.channel.id,
            msg.id,
            header,
            points,
            emoji,
            winner.id,
            winners_count,
            end.isoformat(),
            checksum(winner.id, end.isoformat()),
            "active"
        ))
        await db.commit()

    # ✅ START BACKGROUND TASK
    bot.loop.create_task(run_giveaway(gid))

# ================= READY =================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(os.environ["DISCORD_TOKEN"])
