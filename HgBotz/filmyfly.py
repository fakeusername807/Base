from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
import os, re, aiohttp, json
from datetime import datetime 
from pyrogram import Client, filters
from pyrogram.types import Message
from bs4 import BeautifulSoup
import asyncio
from typing import Dict, List

API_ENDPOINT = "https://poster-two-ivory.vercel.app/api?url="

# Util: extract quality and size from title string
def parse_quality_and_size(title_text: str):
    quality, size = "Unknown", "Unknown"
    if "480p" in title_text: quality = "480p-HD"
    elif "HEVC 480p" in title_text: quality = "480p-HEVC"
    elif "HEVC 720p" in title_text: quality = "720p-HEVC"
    elif "HEVC 1080p" in title_text: quality = "1080p-HEVC"
    elif "HEVC 2160p" in title_text: quality = "2160p-HEVC"
    elif "720p" in title_text: quality = "720p-HD"
    elif "1080p" in title_text: quality = "1080p-HD"
    elif "2160p" in title_text: quality = "2160p-HD"
    
    import re
    match = re.search(r"\((\d+(\.\d+)?\s?(MB|GB))\)", title_text)
    if match:
        size = match.group(1)
    return quality, size

# Async fetcher
async def fetch_filmy_json(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(API_ENDPOINT + url) as resp:
            return await resp.json() if resp.status == 200 else {}

# Command handler
@Client.on_message(filters.command("filmy") & filters.all)
async def filmy_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /filmy filmyfly_url")

    input_url = message.command[1]

    try:
        data = await fetch_filmy_json(input_url)
        title = data.get("title", "🎬 Movie Title")
        cloud_links = data.get("cloud_links", {})

        if not cloud_links:
            return await message.reply("❌ No links found.")

        for key, file_info in cloud_links.items():
            file_title = file_info.get("title", "🎞️ File")
            download_links = file_info.get("download_links", {})

            # Guess quality and size
            quality, size = parse_quality_and_size(file_title)

            # Format text
            text = f"""📌 <b>Title:</b> {file_title}

🔹 <b>Quality:</b> {quality} 

"""

            # Pretty label matching
            for name, url in download_links.items():
                name_lower = name.lower()
                if "gofile" in name_lower:
                    text += f"🔰 <b>GoFile Link: {url}</b>\n\n"
                elif "fast cloud-02" in name_lower:
                    text += f"📥 <b>Fast Server-02: <a href='{url}'> Download Link</a></b>\n\n"
                elif "fast cloud" in name_lower:
                    text += f"📥 <b>Fast Server: <a href='{url}'> Download Link</a></b>\n\n"
                elif "direct" in name_lower or "ddl" in name_lower:
                    text += f"📥 <b>DDL Server: <a href='{url}'> Download Link</a></b>\n\n"
                elif "gdf" in name_lower:
                    text += f"☁️ <b>GDFLIX Server: <a href='{url}'> Download Link</a></b>\n\n"
                elif "watch" in name_lower or "online" in name_lower:
                    text += f"🎦 <b>Watch Online: <a href='{url}'> Download Link</a></b>\n\n"
                elif "telegram" in name_lower:
                    text += f"📦 <b>Telegram File: <a href='{url}'> Download Link</a></b>\n\n"
                else:
                    text += f"🔗 <b>{name}: <a href='{url}'> Download Link</a></b>\n\n"

            text += "<b><blockquote>🌐 Scraped from [FilmyFly](https://telegram.me/MrSagarBots)</blockquote></b>"

            await message.reply(text)

    except Exception as e:
        await message.reply(f"❌ Error: {e}")


# Configuration
BASE_URL = "https://filmyfly.reisen/"
STATE_FILE = "filmyfly_state.json"
TARGET_CHANNEL = -1002756844590  # Your channel ID
ADMIN_ID = 7965786027  # Your admin ID
CHECK_INTERVAL = 600  # 30 minutes in seconds

# Load processed URLs
def load_ff_processed_urls():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"processed_urls": []}

# Save processed URLs
def save_ff_processed_urls(urls):
    with open(STATE_FILE, "w") as f:
        json.dump({"processed_urls": urls}, f)

# Get latest movies from homepage
async def get_latest_ff_movies():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL, timeout=20) as resp:
                if resp.status != 200:
                    return []
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        fmvideo_divs = soup.find_all("div", class_="A10")
        
        movies = []
        for div in fmvideo_divs[:15]:  # Get latest 15 movies
            a_tag = div.find("a")
            if a_tag:
                
                url = a_tag.get("href", "").strip()
                if url and not url.startswith("http"):
                    url = BASE_URL + url
                movies.append({"url": url})
        
        return movies

    except Exception:
        return []

# Process and send movie to channel
async def process_and_send_ff_movie(client: Client, input_url: str):
    try:
        data = await fetch_filmy_json(input_url)
        title = data.get("title", "🎬 Movie Title")
        cloud_links = data.get("cloud_links", {})

        if not cloud_links:
            return await message.reply("❌ No links found.")

        for key, file_info in cloud_links.items():
            file_title = file_info.get("title", "🎞️ File")
            download_links = file_info.get("download_links", {})

            # Guess quality and size
            quality, size = parse_quality_and_size(file_title)

            # Format text
            text = f"""🎬 <b>New Post Just Dropped!</b> ✅

📌 <b>Title:</b> {file_title}

🔹 <b>Quality:</b> {quality} 

"""

            # Pretty label matching
            for name, url in download_links.items():
                name_lower = name.lower()
                if "gofile" in name_lower:
                    text += f"🔰 <b>GoFile Link: {url}</b>\n\n"
                elif "fast cloud-02" in name_lower:
                    text += f"📥 <b>Fast Server-02: <a href='{url}'> Download Link</a></b>\n\n"
                elif "fast cloud" in name_lower:
                    text += f"📥 <b>Fast Server: <a href='{url}'> Download Link</a></b>\n\n"
                elif "direct" in name_lower or "ddl" in name_lower:
                    text += f"📥 <b>DDL Server: <a href='{url}'> Download Link</a></b>\n\n"
                elif "gdf" in name_lower:
                    text += f"☁️ <b>GDFLIX Server: <a href='{url}'> Download Link</a></b>\n\n"
                elif "watch" in name_lower or "online" in name_lower:
                    text += f"🎦 <b>Watch Online: <a href='{url}'> Download Link</a></b>\n\n"
                elif "telegram" in name_lower:
                    text += f"📦 <b>Telegram File: <a href='{url}'> Download Link</a></b>\n\n"
                else:
                    text += f"🔗 <b>{name}: <a href='{url}'> Download Link</a></b>\n\n"

            text += "<b><blockquote>🌐 Scraped from [FilmyFly](https://telegram.me/MrSagarBots)</blockquote></b>"

            await client.send_message(
            chat_id=TARGET_CHANNEL,
            text=text,
            disable_web_page_preview=True
        )
        print(f"Posted new movie: {title}")
        
    except Exception as e:
        print(f"Error processing movie: {e}")

# Background monitoring task
async def monitor_new_ffly_movies(client: Client):
    print("🎥 Movie monitoring started...")
    state = load_ff_processed_urls()
    processed_urls = set(state["processed_urls"])
    
    while True:
        try:
            print("🔍 Checking for new movies...")
            movies = await get_latest_ff_movies()
            new_movies = [m for m in movies if m["url"] not in processed_urls]
            
            if new_movies:
                print(f"🎉 Found {len(new_movies)} new movies!")
                # Process in reverse order to send oldest first
                for movie in reversed(new_movies):
                    await process_and_send_ff_movie(client, movie["url"])
                    processed_urls.add(movie["url"])
                    # Update state after each movie to prevent loss on crash
                    save_ff_processed_urls(list(processed_urls))
                    await asyncio.sleep(10)  # Delay between processing
            else:
                print("🔄 No new movies found")
                
        except Exception as e:
            print(f"⚠️ Monitoring error: {e}")
            
        await asyncio.sleep(CHECK_INTERVAL)
