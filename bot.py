import os
import threading
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask

# ================== FLASK (KEEP ALIVE) ==================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive."

def run_flask():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_flask, daemon=True).start()

# ================== CONFIG ==================
VANITY_TEXT = ".gg/xruqjytycq"
ROLE_ID = 1454892024410017854
LOG_CHANNEL_ID = 1455937616120778844

# ================== DISCORD ==================
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================== READY ==================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🟢 Logged in as {bot.user}")

# ================== VANITY STATUS HANDLER ==================
@bot.event
async def on_presence_update(before, after):
    if not after or not after.guild:
        return

    member = after
    guild = after.guild
    role = guild.get_role(ROLE_ID)
    log_channel = guild.get_channel(LOG_CHANNEL_ID)

    if not role:
        return

    # Get custom status
    custom_status = None
    for activity in after.activities:
        if activity.type == discord.ActivityType.custom:
            custom_status = activity
            break

    status_text = (custom_status.state or "").lower() if custom_status else ""
    has_vanity = VANITY_TEXT in status_text
    had_role = role in member.roles

    try:
        # ➕ Vanity added
        if has_vanity and not had_role:
            await member.add_roles(role, reason="Vanity status detected")

            embed = discord.Embed(
                description=(
                    "**Thank you for supporting us.**\n\n"
                    "You added `.gg/xRuqjytyCQ` to your status —\n"
                    "you now have **pic & gif permissions**.\n\n"
                    "Enjoy the perks 🖤"
                ),
                color=discord.Color.dark_grey()
            )

            embed.set_author(
                name="Vanity Perks Unlocked",
                icon_url=guild.icon.url if guild.icon else None
            )

            # DM user
            try:
                await member.send(embed=embed)
            except:
                pass

            # Log channel
            if log_channel:
                await log_channel.send(embed=embed)

        # ➖ Vanity removed
        elif not has_vanity and had_role:
            await member.remove_roles(role, reason="Vanity status removed")

    except Exception as e:
        print("Error:", e)

# ================== /vanity COMMAND ==================
@bot.tree.command(name="vanity", description="Show vanity status reward info")
async def vanity(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = discord.Embed(
        description="**put `.gg/xRuqjytyCQ` in your status for pic n gif perms**",
        color=discord.Color.dark_grey()
    )

    embed.set_author(
        name="Vanity Access",
        icon_url=interaction.guild.icon.url if interaction.guild.icon else None
    )

    await interaction.followup.send(embed=embed)

# ================== /join COMMAND ==================
@bot.tree.command(name="join", description="Bot joins your voice channel and stays idle")
async def join(interaction: discord.Interaction):
    await interaction.response.defer()

    if not interaction.user.voice or not interaction.user.voice.channel:
        return await interaction.followup.send(
            "❌ You must be in a voice channel.",
            ephemeral=True
        )

    if interaction.guild.voice_client:
        return await interaction.followup.send(
            "⚠️ I'm already in a voice channel.",
            ephemeral=True
        )

    channel = interaction.user.voice.channel
    await channel.connect()

    await interaction.followup.send(
        f"🖤 Joined **{channel.name}** and chilling 24/7."
    )

# ================== START BOT ==================
bot.run(os.getenv("DISCORD_TOKEN"))
