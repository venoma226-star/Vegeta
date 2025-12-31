import os
import discord
from discord.ext import commands
from discord import app_commands

# 🔧 CONFIG
VANITY_TEXT = ".gg/xruqjytycq"
ROLE_ID = 1454892024410017854
LOG_CHANNEL_ID = 1455937616120778844

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.presences = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🟢 Logged in as {bot.user}")

# 🔁 Vanity status logic (unchanged)
@bot.event
async def on_presence_update(before, after):
    if not after or not after.guild:
        return

    member = after
    guild = after.guild
    role = guild.get_role(ROLE_ID)
    log_channel = guild.get_channel(LOG_CHANNEL_ID)

    if role is None:
        return

    custom_status = None
    for activity in after.activities:
        if activity.type == discord.ActivityType.custom:
            custom_status = activity
            break

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

            embed.set_author(
                name="Vanity Perks Unlocked",
                icon_url=guild.icon.url if guild.icon else None
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

# ✨ /vanity command
@bot.tree.command(name="vanity", description="Show vanity status reward info")
async def vanity(interaction: discord.Interaction):
    embed = discord.Embed(
        description="**put `.gg/xRuqjytyCQ` in your status for pic n gif perms**",
        color=discord.Color.dark_grey()
    )
    await interaction.response.send_message(embed=embed)

# 🔊 /join command (SILENT)
@bot.tree.command(name="join", description="Bot joins your voice channel and stays idle")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice or not interaction.user.voice.channel:
        return await interaction.response.send_message(
            "❌ You must be in a voice channel.",
            ephemeral=True
        )

    channel = interaction.user.voice.channel

    if interaction.guild.voice_client:
        return await interaction.response.send_message(
            "⚠️ I'm already in a voice channel.",
            ephemeral=True
        )

    await channel.connect()
    await interaction.response.send_message(
        f"🖤 Joined **{channel.name}** and chilling 24/7."
    )

bot.run(os.getenv("DISCORD_TOKEN"))
