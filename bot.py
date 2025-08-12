import os
import asyncio
from functools import partial

from pyrogram import Client, filters, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from yt_dlp import YoutubeDL
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

# ---------------- CONFIG ---------------- #
API_ID = 23212132
API_HASH = "1c17efa86bdef8f806ed70e81b473c20"
BOT_TOKEN = "8013665655:AAFx7scUcoYtCEktmIfiZaqcqUPLUYKQnQ8"
SESSION_STRING = "BQGvJ_0Adt6lmVaTljo96G9YV0xaOi0O26V2utMXtqO1d9cySnNMh1KCQh2oqT2rxMwDjTj274JF5QDUOF1wO21nH52TvrOuqDvnuZbiOsKM7o4XeTS5CLmwJFAP0IKDvAvEgCnfVGLBGuaOJEijZNaP4nhFvtMP_sMLYjLATOsJHZLEkdz4PkJyfQZCMTV6MSR1D7BFnythV1VTBRA7qIjqYenmEZzGVHXGy4DaetN-BbDwJZmf2QIIZx90Q2-zvFl_z7-2srBWXcOYYDT5pZ1UkwtX71c1hChhmuFJHhLejZz0PWoTUyVr35GRto9J5QU4D0xGvdTaw8qi7m7qe5Gk4IZkjQAAAAHdw02OAA"

# ---------------- CLIENTS ---------------- #
bot = Client("yt_music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("user_session", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call = PyTgCalls(user)

# ---------------- GLOBALS ---------------- #
queue = []
is_playing = False

# ---------------- YTDL OPTIONS ---------------- #
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'opus',
        'preferredquality': '192',
    }],
}

# ---------------- DOWNLOAD FUNCTION ---------------- #
async def download_yt_audio(url):
    loop = asyncio.get_event_loop()
    ydl = YoutubeDL(ydl_opts)
    func = partial(ydl.extract_info, url, download=True)
    data = await loop.run_in_executor(None, func)
    file_path = ydl.prepare_filename(data).replace(".webm", ".opus").replace(".m4a", ".opus")
    return file_path, data.get("title", "Unknown Title")

# ---------------- PLAY FUNCTION ---------------- #
async def play_music(chat_id):
    global is_playing
    if not queue:
        is_playing = False
        await call.leave_group_call(chat_id)
        return

    is_playing = True
    url, title, msg = queue.pop(0)

    try:
        file_path, title = await download_yt_audio(url)
        await call.join_group_call(
            chat_id,
            AudioPiped(file_path)
        )
        await msg.reply(f"🎶 Now Playing: **{title}**", disable_web_page_preview=True)
    except Exception as e:
        await msg.reply(f"❌ Error: {e}")
        is_playing = False
        return

# ---------------- COMMANDS ---------------- #
@bot.on_message(filters.command("start"))
async def start_cmd(_, msg: Message):
    await msg.reply(
        "🎵 **YouTube VC Music Bot**\n"
        "Commands:\n"
        "• `/play query or link` - Play or queue a song\n"
        "• `/skip` - Skip current track\n"
        "• `/queue` - Show queue",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Support", url="https://t.me/yourgroup")]
        ])
    )

@bot.on_message(filters.command("play"))
async def play_cmd(_, msg: Message):
    if len(msg.command) < 2:
        return await msg.reply("❗ Usage: `/play [song name or YouTube link]`")
    
    query = " ".join(msg.command[1:])
    url = None

    # Direct YouTube link
    if "youtube.com" in query or "youtu.be" in query:
        url = query
    else:
        # Search on YouTube
        ydl = YoutubeDL({'format': 'bestaudio', 'quiet': True})
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        if info["entries"]:
            url = info["entries"][0]["webpage_url"]

    if not url:
        return await msg.reply("❌ No results found.")

    queue.append((url, query, msg))
    await msg.reply(f"✅ Queued: **{query}**")

    if not is_playing:
        await play_music(msg.chat.id)

@bot.on_message(filters.command("skip"))
async def skip_cmd(_, msg: Message):
    global is_playing
    if not is_playing:
        return await msg.reply("❌ No song is currently playing.")

    await call.leave_group_call(msg.chat.id)
    is_playing = False
    await msg.reply("⏭ Skipped.")
    await play_music(msg.chat.id)

@bot.on_message(filters.command("queue"))
async def queue_cmd(_, msg: Message):
    if not queue:
        return await msg.reply("📭 Queue is empty.")
    text = "\n".join([f"**{i+1}.** {title}" for i, (_, title, _) in enumerate(queue)])
    await msg.reply(f"📋 **Current Queue:**\n{text}")

# ---------------- MAIN ---------------- #
if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    
    print("Starting bot...")
    bot.start()
    user.start()
    call.start()
    idle()
