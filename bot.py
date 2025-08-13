import asyncio
import re
from collections import defaultdict
from typing import Dict, List, Tuple

from pyrogram import Client, filters, idle
from pyrogram.types import Message
from yt_dlp import YoutubeDL

from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.exceptions import PytgcallsError

# ---------------- CONFIG ---------------- #
API_ID = 23212132
API_HASH = "1c17efa86bdef8f806ed70e81b473c20"
BOT_TOKEN = "8013665655:AAFx7scUcoYtCEktmIfiZaqcqUPLUYKQnQ8"
SESSION_STRING = "BQGvJ_0Adt6lmVaTljo96G9YV0xaOi0O26V2utMXtqO1d9cySnNMh1KCQh2oqT2rxMwDjTj274JF5QDUOF1wO21nH52TvrOuqDvnuZbiOsKM7o4XeTS5CLmwJFAP0IKDvAvEgCnfVGLBGuaOJEijZNaP4nhFvtMP_sMLYjLATOsJHZLEkdz4PkJyfQZCMTV6MSR1D7BFnythV1VTBRA7qIjqYenmEZzGVHXGy4DaetN-BbDwJZmf2QIIZx90Q2-zvFl_z7-2srBWXcOYYDT5pZ1UkwtX71c1hChhmuFJHhLejZz0PWoTUyVr35GRto9J5QU4D0xGvdTaw8qi7m7qe5Gk4IZkjQAAAAHdw02OAA"

# ---------------- CLIENTS ---------------- #
# Bot for commands
bot = Client("yt_music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
# User session to join/play in voice chats
user = Client("user_session", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
# PyTgCalls bound to the user session
calls = PyTgCalls(user)

# ---------------- STATE ---------------- #
# Per-chat queue: chat_id -> list of (url, title, requester_id)
queues: Dict[int, List[Tuple[str, str, int]]] = defaultdict(list)
# Chats currently playing (i.e., already joined VC and streaming)
playing_chats: Dict[int, bool] = defaultdict(bool)
# A lock per chat to serialize start/skip actions
locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

# ---------------- HELPERS ---------------- #
YDL_OPTS = {"quiet": True, "noplaylist": True, "format": "bestaudio/best"}

yt_regex = re.compile(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/", re.IGNORECASE)


def is_yt_link(text: str) -> bool:
    return bool(yt_regex.search(text))


def search_youtube(query: str):
    """Return (url, title)."""
    with YoutubeDL(YDL_OPTS) as ydl:
        if is_yt_link(query):
            info = ydl.extract_info(query, download=False)
        else:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if "entries" in info and info["entries"]:
                info = info["entries"][0]
        url = info.get("webpage_url") or info.get("url")
        title = info.get("title") or "Unknown Title"
        if not url:
            raise ValueError("No playable URL found.")
        return url, title


async def start_or_continue(chat_id: int, msg: Message):
    """If nothing is playing in this chat, start playing the first item in queue."""
    async with locks[chat_id]:
        if playing_chats[chat_id]:
            return  # already playing
        if not queues[chat_id]:
            return

        url, title, _ = queues[chat_id][0]
        try:
            # Join VC and play
            await calls.join_group_call(chat_id, AudioPiped(url))
            playing_chats[chat_id] = True
            await msg.reply(f"🎶 **Now playing:** {title}")
        except PytgcallsError as e:
            playing_chats[chat_id] = False
            await msg.reply(f"❌ Failed to join/play in voice chat:\n`{e}`")
        except Exception as e:
            playing_chats[chat_id] = False
            await msg.reply(f"❌ Unexpected error:\n`{e}`")


async def play_next(chat_id: int, msg: Message):
    """Pop current and play next in queue, or stop if empty."""
    async with locks[chat_id]:
        if queues[chat_id]:
            queues[chat_id].pop(0)

        if not queues[chat_id]:
            # Nothing left: leave VC
            try:
                await calls.leave_group_call(chat_id)
            except Exception:
                pass
            playing_chats[chat_id] = False
            await msg.reply("✅ Queue finished. Left voice chat.")
            return

        next_url, next_title, _ = queues[chat_id][0]
        try:
            await calls.change_stream(chat_id, AudioPiped(next_url))
            playing_chats[chat_id] = True
            await msg.reply(f"⏭ **Skipped. Now playing:** {next_title}")
        except PytgcallsError as e:
            playing_chats[chat_id] = False
            await msg.reply(f"❌ Couldn’t switch track:\n`{e}`")
        except Exception as e:
            playing_chats[chat_id] = False
            await msg.reply(f"❌ Unexpected error:\n`{e}`")


# ---------------- COMMANDS ---------------- #
@bot.on_message(filters.command("play") & filters.group)
async def cmd_play(_, msg: Message):
    chat_id = msg.chat.id
    if len(msg.command) < 2:
        await msg.reply("❗ Usage: `/play [YouTube link or search query]`", quote=True)
        return

    query = " ".join(msg.command[1:])
    try:
        url, title = search_youtube(query)
    except Exception as e:
        await msg.reply(f"❌ No results or not playable:\n`{e}`", quote=True)
        return

    queues[chat_id].append((url, title, msg.from_user.id if msg.from_user else 0))
    pos = len(queues[chat_id])
    if playing_chats[chat_id]:
        await msg.reply(f"✅ **Queued:** {title}\n📍 Position: `{pos}`", quote=True)
    else:
        await msg.reply(f"✅ **Queued & starting:** {title}", quote=True)
        await start_or_continue(chat_id, msg)


@bot.on_message(filters.command(["skip", "next"]) & filters.group)
async def cmd_skip(_, msg: Message):
    chat_id = msg.chat.id
    if not playing_chats[chat_id] or not queues[chat_id]:
        await msg.reply("❌ Nothing is playing.", quote=True)
        return
    await play_next(chat_id, msg)


@bot.on_message(filters.command("queue") & filters.group)
async def cmd_queue(_, msg: Message):
    chat_id = msg.chat.id
    q = queues[chat_id]
    if not q:
        await msg.reply("📭 Queue is empty.", quote=True)
        return
    lines = [f"**Now**: {q[0][1]}"] + [f"{i}. {t}" for i, (_, t, _) in enumerate(q[1:], start=1)]
    await msg.reply("📋 **Current Queue**:\n" + "\n".join(lines), quote=True)


@bot.on_message(filters.command(["stop", "end"]) & filters.group)
async def cmd_stop(_, msg: Message):
    chat_id = msg.chat.id
    queues[chat_id].clear()
    try:
        await calls.leave_group_call(chat_id)
    except Exception:
        pass
    playing_chats[chat_id] = False
    await msg.reply("🛑 Stopped and left voice chat.", quote=True)


@bot.on_message(filters.command("help"))
async def cmd_help(_, msg: Message):
    await msg.reply(
        "**YouTube Music Bot**\n"
        "Commands:\n"
        "• `/play <link or query>` — play or queue a song\n"
        "• `/skip` — skip to next\n"
        "• `/queue` — show queue\n"
        "• `/stop` — clear queue and leave VC\n"
        "\n_Bot uses your user session to join VC. Make sure that account is in the group._",
        quote=True,
    )


# ---------------- MAIN ---------------- #
async def main():
    await bot.start()
    await user.start()
    await calls.start()

    print("Bot is up. Waiting for commands…")
    await idle()

    await calls.stop()
    await bot.stop()
    await user.stop()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
