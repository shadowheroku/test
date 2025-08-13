import asyncio
import re
from collections import defaultdict
from typing import Dict, List, Tuple

from pyrogram import Client, filters, idle
from pyrogram.types import Message
from yt_dlp import YoutubeDL

from pytgcalls import PyTgCalls

from pytgcalls.exceptions import PytgcallsError

# ---------------- CONFIG ---------------- #
API_ID = 23212132
API_HASH = "1c17efa86bdef8f806ed70e81b473c20"
BOT_TOKEN = "8013665655:AAFx7scUcoYtCEktmIfiZaqcqUPLUYKQnQ8"
SESSION_STRING = "BQGvJ_0Adt6lmVaTljo96G9YV0xaOi0O26V2utMXtqO1d9cySnNMh1KCQh2oqT2rxMwDjTj274JF5QDUOF1wO21nH52TvrOuqDvnuZbiOsKM7o4XeTS5CLmwJFAP0IKDvAvEgCnfVGLBGuaOJEijZNaP4nhFvtMP_sMLYjLATOsJHZLEkdz4PkJyfQZCMTV6MSR1D7BFnythV1VTBRA7qIjqYenmEZzGVHXGy4DaetN-BbDwJZmf2QIIZx90Q2-zvFl_z7-2srBWXcOYYDT5pZ1UkwtX71c1hChhmuFJHhLejZz0PWoTUyVr35GRto9J5QU4D0xGvdTaw8qi7m7qe5Gk4IZkjQAAAAHdw02OAA"

# ---------------- CLIENTS ---------------- #
import os
import asyncio
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, HighQualityVideo

# Configuration  # Replace with your user session string
YOUTUBE_COOKIE = """ # Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.youtube.com	TRUE	/	FALSE	1789394960	HSID	A6ZfyYUep0Np9MQw1
.youtube.com	TRUE	/	TRUE	1789394960	SSID	Agye2vfnm-dkrucAt
.youtube.com	TRUE	/	FALSE	1789394960	APISID	kz7E2afizJqVhEVm/AO-71rWNJbOrr03lY
.youtube.com	TRUE	/	TRUE	1789394960	SAPISID	7fJ-lvyh4STWCBvz/Adsi-bKLNu39ch5Wh
.youtube.com	TRUE	/	TRUE	1789394960	__Secure-1PAPISID	7fJ-lvyh4STWCBvz/Adsi-bKLNu39ch5Wh
.youtube.com	TRUE	/	TRUE	1789394960	__Secure-3PAPISID	7fJ-lvyh4STWCBvz/Adsi-bKLNu39ch5Wh
.youtube.com	TRUE	/	TRUE	1777881466	LOGIN_INFO	AFmmF2swRAIgDG6w06DO6jzGmopZi4YYYaDhOoEY4gB5zstRy3l5-zkCIHcUr0KOk-7uvH446znpbL79FTkyI348bB0GXULReZdc:QUQ3MjNmeVpIUXUzSXhOV0l1aHRNMFV2dVE0ckJjRG15VnFPVnNRWEh3UUpGQnpyX1RNZDZtRkduZ0pxclducjMzOVEwcWI2dWJPY3BnSnNSd2U0NHRmQlJJYjljY29hcV9iemhKblhUVDN0NGdIQzdOcUVWZmd6M3NtQ20wU1hoUUtsVS1zWENUcDNuU2E2YkM1dU9rREI2NWVDbXB3OVhR
.youtube.com	TRUE	/	FALSE	1779724239	_ga	GA1.1.1034053585.1745164239
.youtube.com	TRUE	/	TRUE	1789663650	PREF	f4=4000000&f6=40000000&tz=Asia.Calcutta&f7=150&repeat=NONE&autoplay=true
.youtube.com	TRUE	/	FALSE	1779724472	_ga_VCGEPY40VB	GS1.1.1745164238.1.1.1745164471.60.0.0
.youtube.com	TRUE	/	FALSE	1789394960	SID	g.a0000AjzvmDVdcaAaK1FXG6J6NdEurHHeyqSwjCWLIYz3KFegHsV1dE2o6KB33rpb_7g4EETTwACgYKASgSARESFQHGX2Miuat42fzbV_FlDrWm7uO5uhoVAUF8yKpdsOfPj1S0UexoyV_vrSKm0076
.youtube.com	TRUE	/	TRUE	1789394960	__Secure-1PSID	g.a0000AjzvmDVdcaAaK1FXG6J6NdEurHHeyqSwjCWLIYz3KFegHsVXiz1bbBKw2CtB1qgIa3yMwACgYKATsSARESFQHGX2Mi4Bb47FQb7KtwstoGlnPu5BoVAUF8yKospSKEGprHVlU1MWg9X8OY0076
.youtube.com	TRUE	/	TRUE	1789394960	__Secure-3PSID	g.a0000AjzvmDVdcaAaK1FXG6J6NdEurHHeyqSwjCWLIYz3KFegHsVD9L5Es1hvyFBrrSUHltu1AACgYKAeASARESFQHGX2Mi3-d_L7JlUeEUkEoBBNB7ixoVAUF8yKqmRh47rBnVkvAEjDwFQBOi0076
.youtube.com	TRUE	/	TRUE	1755104250	CONSISTENCY	AKreu9u6y9wMKQxS36AddNUQnO_A_Ji8iUBznXoJRZfmhLqSR4wznXPTK-sjZvwEsLYIgwAX8RMPQEb8L8thCMiNHEg5UTsE84DnHOJ0WrSzjP9MbqE5yJ2nNqj6RCEGkOAgUvbMIgQao-5M1qmC5aH3
.youtube.com	TRUE	/	TRUE	1770914851	NID	525=FiuPHv4oT9_PoH-OX2BVcjJM6JkLnfzyZeamY6iTPu_wrO_vSzMRp6rctM3_PZsJ_H0AcU31EsdtE2qPtwyc8okVQzBK01EV_fLkeIxdxznMJx1mo1iz-Bf392ntybskV_KNnkaVceUJZrS3AHVJ4mYjG3yCcKsE2lDsZWZQnMrB6ZkHk_HL4mQ6VuIqXcBmPWE9ozfc3YgcLpGLTUqR8S0XHQU3rgg
.youtube.com	TRUE	/	TRUE	1786639653	__Secure-1PSIDTS	sidts-CjEB5H03Pym5VB0yk-lhUcNllQ2TBVEkBE9aupm4S3YtXudIh8D7_cO__7lgwWZSmOt3EAA
.youtube.com	TRUE	/	TRUE	1786639653	__Secure-3PSIDTS	sidts-CjEB5H03Pym5VB0yk-lhUcNllQ2TBVEkBE9aupm4S3YtXudIh8D7_cO__7lgwWZSmOt3EAA
.youtube.com	TRUE	/	FALSE	1786639654	SIDCC	AKEyXzWRiBQUuUGhFjAmPQ9ZhA263WMPAx13CppF0Z9SwRHQPXgF-hc1zY0Ko5nqqI_nBxneTGs
.youtube.com	TRUE	/	TRUE	1786639654	__Secure-1PSIDCC	AKEyXzULMeYwnSxB-cU27TiFSRqgy0pwmymtM5W84wGwSJ9foj4DTYrawABESxhhIU-Rsvk1Tno
.youtube.com	TRUE	/	TRUE	1786639654	__Secure-3PSIDCC	AKEyXzXG1B63d3j3C2_Nq3xrM3CZIxg4yQLB4xK0txA3MApixBfqWsugCmuYSWiOGtqKGeFkitM
.youtube.com	TRUE	/	TRUE	1770655654	VISITOR_INFO1_LIVE	PXh3lLWceIU
.youtube.com	TRUE	/	TRUE	1770655654	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgKQ%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	faZFj2ZfkW8
.youtube.com	TRUE	/	TRUE	1770655647	__Secure-ROLLOUT_TOKEN	CPWMs-mStNuj7gEQtImonuWvjAMY8fL4zJ6IjwM%3D
"""  # Replace with your YouTube cookies

# Initialize clients
bot = Client(
    "musicbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

user = Client(
    "userbot",
    session_string=SESSION_STRING,
    api_id=API_ID,
    api_hash=API_HASH
)

pytgcalls = PyTgCalls(user)

# Queue system
queues = {}
current_playing = {}

# YouTube DL options with cookies
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
    'cookiefile': 'cookies.txt',  # Save cookies to file
    'extract_flat': True,
    'noplaylist': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# Initialize cookies file
if YOUTUBE_COOKIE:
    with open('cookies.txt', 'w') as f:
        f.write(YOUTUBE_COOKIE)

async def download_and_extract_info(query: str):
    """Download audio and extract info using yt-dlp with cookies"""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = await asyncio.to_thread(ydl.extract_info, query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            return info
        except Exception as e:
            print(f"Error extracting info: {e}")
            return None

async def play_next(chat_id: int):
    """Play next song in queue"""
    if chat_id in queues and len(queues[chat_id]) > 0:
        song = queues[chat_id].pop(0)
        await play_song(chat_id, song)
    else:
        current_playing.pop(chat_id, None)

async def play_song(chat_id: int, song_info: dict):
    """Play the song in voice chat"""
    try:
        url = song_info['url']
        title = song_info['title']
        
        # Update current playing
        current_playing[chat_id] = title
        
        # Join voice chat if not already joined
        try:
            await pytgcalls.join_group_call(
                chat_id,
                AudioPiped(
                    url,
                    HighQualityAudio(),
                )
            )
        except Exception as e:
            print(f"Error joining call: {e}")
            # Try with video if audio fails (some links work better this way)
            await pytgcalls.join_group_call(
                chat_id,
                AudioVideoPiped(
                    url,
                    HighQualityAudio(),
                    HighQualityVideo(),
                )
            )
        
        # Notify chat
        await bot.send_message(chat_id, f"🎶 Now playing: **{title}**")
        
    except Exception as e:
        print(f"Error playing song: {e}")
        await bot.send_message(chat_id, "❌ Failed to play the song.")
        await play_next(chat_id)

@bot.on_message(filters.command("play") & filters.group)
async def play_command(client: Client, message: Message):
    """Handle /play command"""
    chat_id = message.chat.id
    query = " ".join(message.command[1:])
    
    if not query:
        await message.reply("Please provide a song name or YouTube URL after /play")
        return
    
    # Check if user is in voice chat
    try:
        member = await message.chat.get_member(message.from_user.id)
        if not member.voice or not member.voice.chat:
            await message.reply("You need to join the voice chat first!")
            return
    except PeerIdInvalid:
        pass  # Skip check in private chats
    
    # Add to queue
    if chat_id not in queues:
        queues[chat_id] = []
    
    # Show searching message
    msg = await message.reply("🔍 Searching and processing... (this will be fast with cookies)")
    
    # Get song info
    song_info = await download_and_extract_info(query)
    if not song_info:
        await msg.edit("❌ Could not find or process the song.")
        return
    
    # Add to queue
    queues[chat_id].append({
        'url': song_info['url'],
        'title': song_info['title'],
    })
    
    await msg.edit(f"✅ Added to queue: **{song_info['title']}**")
    
    # Play immediately if nothing is playing
    if chat_id not in current_playing:
        await play_next(chat_id)

@bot.on_message(filters.command("skip") & filters.group)
async def skip_command(client: Client, message: Message):
    """Handle /skip command"""
    chat_id = message.chat.id
    
    if chat_id not in current_playing:
        await message.reply("❌ Nothing is currently playing.")
        return
    
    try:
        await pytgcalls.leave_group_call(chat_id)
        await message.reply("⏩ Skipped current song.")
        await play_next(chat_id)
    except Exception as e:
        await message.reply(f"❌ Failed to skip: {e}")

@bot.on_message(filters.command("queue") & filters.group)
async def queue_command(client: Client, message: Message):
    """Handle /queue command"""
    chat_id = message.chat.id
    
    if chat_id not in queues or not queues[chat_id]:
        await message.reply("❌ Queue is empty.")
        return
    
    queue_text = "🎶 Current Queue:\n"
    if chat_id in current_playing:
        queue_text += f"▶️ Now Playing: {current_playing[chat_id]}\n\n"
    
    for i, song in enumerate(queues[chat_id], 1):
        queue_text += f"{i}. {song['title']}\n"
    
    await message.reply(queue_text)

@pytgcalls.on_stream_end()
async def on_stream_end(update: Update):
    """Handle when stream ends"""
    chat_id = update.chat_id
    await play_next(chat_id)

async def main():
    """Start the clients"""
    await bot.start()
    await user.start()
    await pytgcalls.start()
    print("Bot started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
