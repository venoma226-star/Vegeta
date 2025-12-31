import os
import threading
import discord
from discord.ext import commands
from flask import Flask

# ================== FLASK ==================
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
GUILD_ID = 123456789012345678  # 🔴 PUT YOUR SERVER ID HERE

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
    guild = discord.Object(id=GUILD_ID)
    bot.tree.copy_global_to(guild=guild)
    await bot.tree.sync(guild=guild)
    print(f"🟢 Logged in as {bot.user}")

# ================== VANITY STATUS ==================
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

    custom_status = next(
        (a for a in after.activities if a.type == discord.ActivityType.custom),
        None
    )

    status_text = (custom_status.state or "").lower() if custom_status else ""
    has_vanity = VANITY_TEXT in status_text
    had_role = role in member.roles

    try:
        if has_vanity and not had_role:
            await member.add_roles(role)

            embed = discord.Embed(
                description=(
                    "**Thank you for supporting us.**\n\n"
                    "You added `.gg/xRuqjytyCQ` to your status —\n"
                    "you now have **pic & gif permissions**.\n\n"
                    "Enjoy the perks 🖤"
                ),
                color=discord.Color.dark_grey()
            )

            try:
                await member.send(embed=embed)
            except:
                pass

            if log_channel:
                await log_channel.send(embed=embed)

        elif not has_vanity and had_role:
            await member.remove_roles(role)

    except Exception as e:
        print("Error:", e)

# ================== /vanity ==================
@bot.tree.command(name="vanity", description="Vanity status info")
async def vanity(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    embed = discord.Embed(
        description="**put `.gg/xRuqjytyCQ` in your status for pic n gif perms**",
        color=discord.Color.dark_grey()
    )

    await interaction.followup.send(embed=embed)

# ================== /join ==================
@bot.tree.command(name="join", description="Join voice channel silently")
async def join(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)

    if not interaction.user.voice:
        return await interaction.followup.send(
            "❌ You must be in a voice channel.",
            ephemeral=True
        )

    if interaction.guild.voice_client:
        return await interaction.followup.send(
            "⚠️ I'm already in a voice channel.",
            ephemeral=True
        )

    await interaction.user.voice.channel.connect()
    await interaction.followup.send("🖤 Joined VC and chilling 24/7.")

# ================== START ==================
bot.run(os.getenv("DISCORD_TOKEN"))
