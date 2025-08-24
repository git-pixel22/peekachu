import os
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
from dotenv import load_dotenv
from datetime import datetime
import time  # <-- for timing
import psutil  # <-- for memory usage

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ---- Discord Bot ----
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.members = True  # needed to fetch display_name

bot = commands.Bot(command_prefix="!", intents=intents)
bot_ready = asyncio.Event()

# Store active searches per user (user_id -> {"results": [...], "page": int})
active_searches = {}

RESULTS_PER_PAGE = 5


def get_memory_usage_mb():
    """Return current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


def log(msg: str):
    """Simple timestamped logger with memory usage"""
    mem = get_memory_usage_mb()
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg} | 🧠 {mem:.2f} MB")


def build_page_embed(word, limit, results, page):
    """Build an embed for the given page of search results"""
    start = (page - 1) * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    page_results = results[start:end]

    embed = discord.Embed(
        title=f"🔍 Search results for `{word}` (≥ {limit} chars)",
        color=discord.Color.green()
    )

    if not page_results:
        embed.description = "No results on this page."
        return embed

    for i, r in enumerate(page_results, start=start + 1):
        preview = r["content"][:30] + ("...more" if len(r["content"]) > 30 else "")
        embed.add_field(
            name=f"{i}. From @{r['author']} in **#{r['channel']}**",
            value=f"{preview}\n[Jump to message]({r['link']})",
            inline=False
        )

    total_pages = (len(results) + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
    embed.set_footer(text=f"Page {page}/{total_pages}")
    return embed


class SearchPaginationView(View):
    def __init__(self, user_id, word, limit):
        super().__init__(timeout=900)  # 15 min timeout
        self.user_id = user_id
        self.word = word
        self.limit = limit

    async def update_page(self, interaction, delta):
        state = active_searches.get(self.user_id)
        if not state:
            await interaction.response.send_message("This search session expired.", ephemeral=True)
            return

        new_page = state["page"] + delta
        total_pages = (len(state["results"]) + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

        if new_page < 1 or new_page > total_pages:
            await interaction.response.defer()  # ignore invalid clicks
            return

        state["page"] = new_page
        log(f"📄 User {interaction.user} navigated to page {new_page}/{total_pages} of search '{self.word}'")
        embed = build_page_embed(self.word, self.limit, state["results"], new_page)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: Button):
        await self.update_page(interaction, -1)

    @discord.ui.button(label="➡️ Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: Button):
        await self.update_page(interaction, +1)


@bot.tree.command(name="search", description="Search recent messages in all channels")
@app_commands.describe(word="Word to search for", limit="Minimum message length")
async def search_slash(interaction: discord.Interaction, word: str, limit: int = 80):
    start_time = time.time()  # <-- start timing
    log(f"🔎 {interaction.user} triggered /search for '{word}' (≥ {limit} chars)")
    await interaction.response.defer()

    results = []

    for guild in bot.guilds:
        log(f"📂 Searching guild: {guild.name}")
        for channel in guild.text_channels:
            try:
                async for msg in channel.history(limit=500):
                    if msg.author == bot.user:
                        continue
                    if word.lower() in msg.content.lower() and len(msg.content) >= limit:
                        display_name = msg.author.display_name
                        results.append({
                            "content": msg.content,
                            "link": f"https://discord.com/channels/{guild.id}/{channel.id}/{msg.id}",
                            "channel": channel.name,
                            "timestamp": msg.created_at,
                            "author": display_name,
                        })
            except Exception as e:
                log(f"⚠️ Error fetching from channel {channel.name}: {e}")

    elapsed = time.time() - start_time  # <-- end timing

    if not results:
        log(f"❌ No results found for '{word}' (requested by {interaction.user}) "
            f"in {elapsed:.2f}s")
        await interaction.followup.send("No results found.")
        return

    results.sort(key=lambda x: x["timestamp"], reverse=True)
    active_searches[interaction.user.id] = {"results": results, "page": 1}
    log(f"✅ Found {len(results)} results for '{word}' "
        f"(requested by {interaction.user}) in {elapsed:.2f}s")

    embed = build_page_embed(word, limit, results, 1)
    view = SearchPaginationView(interaction.user.id, word, limit)

    await interaction.followup.send(embed=embed, view=view)


@bot.event
async def on_ready():
    log(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    bot_ready.set()
    await bot.tree.sync()
    log("✅ Slash commands synced and bot is ready!")


if __name__ == "__main__":
    asyncio.run(bot.start(TOKEN))