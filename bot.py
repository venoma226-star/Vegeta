import os
import random
import nextcord
from nextcord.ext import tasks, commands
from nextcord import Interaction
from flask import Flask
import threading

# ---------------- CONFIG ----------------
TOKEN = os.environ.get("TOKEN")
CHANNEL_ID = 1448181797786750988
AUTHORIZED_USER = 1355140133661184221

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- 30 LEGENDARY MESSAGES ----------------
epic_lines = [
    "🌟 Albedo rises as the ultimate Saiyan elite! 💗🫂 The cosmos trembles before him! 🌌",
    "🔥 Turles bows before Albedo’s power — unmatched Saiyan supremacy! ⚡",
    "⚡ Gohan trains in awe, inspired by the majestic aura of Albedo! 🌠",
    "🦸‍♂️ Even Superman feels the weight of Albedo’s legendary energy! 💥",
    "🦇 Batman acknowledges: Strategy meets unstoppable Saiyan force in Albedo! 🖤",
    "🤖 Iron Man recalibrates — Albedo’s power exceeds all tech and logic! ✨",
    "💫 Cosmic winds bow to Albedo — the ultimate fusion of Saiyan fury and heroism! 🌌",
    "🌠 Legends unite, but Albedo stands supreme — Saiyan majesty unchallenged! 🔥",
    "🌌 The galaxy shakes as Albedo ascends beyond mortal limits! 🌟",
    "⚡ Turles whispers: None can rival Albedo's Saiyan wrath! 🔥",
    "🌟 Gohan smiles, knowing Albedo defines true Saiyan destiny! ✨",
    "🦸‍♂️ Superman nods in respect to Albedo’s cosmic aura! 💫",
    "🦇 Batman recognizes: Albedo's strategy is pure genius and power! ⚡",
    "🤖 Iron Man upgrades systems, realizing no tech can match Albedo! 🌌",
    "💥 Albedo strikes — even gods watch in awe! 🌠",
    "🔥 Turles’ forces bow before unmatched Saiyan supremacy! ⚡",
    "🌟 Gohan’s training pales before Albedo’s majesty! 💫",
    "🦸‍♂️ Heroes unite, yet none rival Albedo’s presence! 🌌",
    "🦇 Batman prepares for battle… yet Albedo is untouchable! ⚡",
    "🤖 Iron Man calculates… and fails. Albedo surpasses logic! 🔥",
    "💫 Cosmic storms obey the will of Albedo! 🌟",
    "🌠 Legends fall silent — Albedo dominates the battlefield! ⚡",
    "🌌 Albedo’s aura shatters limits across time and space! 🔥",
    "⚡ Turles trembles — the ultimate Saiyan has arrived! 💫",
    "🌟 Gohan bows: Albedo’s power inspires generations! 🌠",
    "🦸‍♂️ Superman contemplates: Could he ever rival Albedo? 🌌",
    "🦇 Batman calculates the odds… but Albedo breaks them all! ⚡",
    "🤖 Iron Man observes: Even the most advanced tech fails against Albedo! 💥",
    "💫 Albedo, Turles, Gohan — legends intertwined in Saiyan glory! 🌟",
    "🌠 The universe itself resonates with Albedo’s majesty! ✨"
]

# ---------------- MESSAGE LOOP ----------------
@tasks.loop(seconds=0.2)
async def majestic_message():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(random.choice(epic_lines))

# ---------------- SLASH COMMANDS ----------------
@bot.slash_command(name="start", description="Start epic Albedo spam")
async def start(interaction: Interaction):
    if interaction.user.id != AUTHORIZED_USER:
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    if majestic_message.is_running():
        await interaction.response.send_message("Epic spam is already running!", ephemeral=True)
    else:
        majestic_message.start()
        await interaction.response.send_message("Epic Albedo spam started! 🌌", ephemeral=True)

@bot.slash_command(name="stop", description="Stop epic Albedo spam")
async def stop(interaction: Interaction):
    if interaction.user.id != AUTHORIZED_USER:
        await interaction.response.send_message("You are not authorized.", ephemeral=True)
        return
    if majestic_message.is_running():
        majestic_message.stop()
        await interaction.response.send_message("Epic Albedo spam stopped! ✨", ephemeral=True)
    else:
        await interaction.response.send_message("Epic spam is not running.", ephemeral=True)

# ---------------- AUTO-RESTART ON DISCONNECT ----------------
@bot.event
async def on_disconnect():
    print("Bot disconnected! Will attempt to reconnect and resume spam...")

@bot.event
async def on_resumed():
    print("Bot reconnected. Resuming majestic spam...")
    if not majestic_message.is_running():
        majestic_message.start()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # Resume spam automatically if bot restarts
    if not majestic_message.is_running():
        majestic_message.start()

# ---------------- FLASK KEEP-ALIVE ----------------
app = Flask("")

@app.route("/")
def home():
    return "Bot is running and majestic! 🌌"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ---------------- RUN BOTH ----------------
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN)
