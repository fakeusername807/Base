import os, re, aiohttp, json
from datetime import datetime 
from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
from bs4 import BeautifulSoup
import asyncio
from typing import Dict, List

# Step 1: Scrape first 3 links
async def scrape_first_three_links(page_url: str) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(page_url, timeout=20) as resp:
                if resp.status != 200:
                    return {"error": f"❌ HTTP Error: {resp.status}"}
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        bolly_div = soup.find("div", class_="Bolly")
        if not bolly_div:
            return {"error": "❌ <div class='Bolly'> not found"}

        a_tags = bolly_div.find_all("a")
        if len(a_tags) < 3:
            return {"error": "❌ Less than 3 links found"}

        result = {
            a_tags[0].text.strip() or "WATCH ONLINE": a_tags[0].get("href", "").strip(),
            a_tags[1].text.strip() or "Google Drive Direct Links": a_tags[1].get("href", "").strip(),
            a_tags[2].text.strip() or "SERVER 01": a_tags[2].get("href", "").strip(),
        }

        return result

    except Exception as e:
        return {"error": f"❌ Exception in main page: {e}"}

# Step 2: Your external link extractor
async def extract_external_links_gdrive(url: str) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=20) as response:
                if response.status != 200:
                    return [f"❌ Failed to fetch: {response.status}"]

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                links = [
                    a["href"].strip()
                    for a in soup.find_all("a", rel="external")
                    if a.has_attr("href")
                ]

        return links if links else ["❌ No external links found."]
    except Exception as e:
        return [f"❌ Exception scraping link: {e}"]


# Final Pyrogram command
@Client.on_message(filters.command("sky") & filters.all)
async def skymovies_full_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /sky skymovieshd_url")

    url = message.command[1]
    M = await message.reply("🔍 ")
    
    pattern = r'.*/(.*)\.html$'
    match = re.match(pattern, url) 
    if match:
        title = match.group(1)
        title = title.replace("-", " ")

    # Step 1: Extract top 3 links
    data = await scrape_first_three_links(url)
    if "error" in data:
        return await message.reply(data["error"])

    watch_url = data.get("WATCH ONLINE")
    gdrive_redirect = data.get("Google Drive Direct Links")
    server01_redirect = data.get("SERVER 01")

    # Step 2: Scrape GDrive & Server01 external links
    gdrive_links = await extract_external_links_gdrive(gdrive_redirect)
    server01_links = await extract_external_links_gdrive(server01_redirect)



        # Step 3: Categorize gofile and others
    gofile_links = []
    normal_links = []

    for link in gdrive_links + server01_links:
        if "gofile.io" in link:
            gofile_links.append(link)
        
    for link in gdrive_links:
        if link.startswith("http"):
            normal_links.append(link)


    # Step 4: Format output
    text = " <b>🎬 New Post Just Dropped! ✅</b>\n\n"
    text += f" <b>Title</b> = <code>{title}</code>\n\n" 
    text += f"<b><blockquote>🐬Stream Tape Link🐬</blockquote> \n {watch_url} \n</b>"
    
    if gofile_links:
        text += "\n<b><blockquote>🔰GoFile Link🔰</blockquote></b>\n"
        for i, link in enumerate(gofile_links, 1):
            text += f"<b>• {link}</b>\n"

    text += "<b><blockquote>Cloud Urls 💥</blockquote></b>\n"
   
    for i, link in enumerate(normal_links, 1):
        text += f"<b>{i}. {link}</b>\n"
 
    text += f"<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>"   
   
    await M.edit_text(text,  disable_web_page_preview=True)



# Configuration
BASE_URL = "https://skymovieshd.land/"
STATE_FILE = "skymovies_state.json"
TARGET_CHANNEL = -1002825305780  # Your channel ID
ADMIN_ID = 7965786027  # Your admin ID
CHECK_INTERVAL = 600  # 30 minutes in seconds

# Load processed URLs
def load_processed_urls():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"processed_urls": []}

# Save processed URLs
def save_processed_urls(urls):
    with open(STATE_FILE, "w") as f:
        json.dump({"processed_urls": urls}, f)


# Get latest movies from homepage
async def get_latest_movies():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL, timeout=20) as resp:
                if resp.status != 200:
                    return []
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        fmvideo_divs = soup.find_all("div", class_="Fmvideo")
        
        movies = []
        for div in fmvideo_divs[:15]:  # Get latest 15 movies
            a_tag = div.find("a")
            if a_tag:
                title = a_tag.text.strip()
                url = a_tag.get("href", "").strip()
                if url and not url.startswith("http"):
                    url = BASE_URL + url
                movies.append({"title": title, "url": url})
        
        return movies

    except Exception:
        return []
        
# Process and send movie to channel
async def process_and_send_movie(client: Client, movie_url: str):
    try:
        pattern = r'.*/(.*)\.html$'
        match = re.match(pattern, movie_url) 
        title = match.group(1) if match else "Unknown Title"
        title = title.replace("-", " ")

        # Step 1: Extract top 3 links
        data = await scrape_first_three_links(movie_url)
        if "error" in data:
            print(f"Error processing {movie_url}: {data['error']}")
            return

        watch_url = data.get("WATCH ONLINE", "")
        gdrive_redirect = data.get("Google Drive Direct Links", "")
        server01_redirect = data.get("SERVER 01", "")

        # Step 2: Scrape GDrive & Server01 external links
        gdrive_links = await extract_external_links_gdrive(gdrive_redirect)
        server01_links = await extract_external_links_gdrive(server01_redirect)

        # Step 3: Categorize links
        gofile_links = [link for link in gdrive_links + server01_links if "gofile.io" in link]
        normal_links = [link for link in gdrive_links if link.startswith("http")]

        # Step 4: Format message
        text = "<b>🎬 New Post Just Dropped! ✅</b>\n\n"
        text += f"<b>📌 Title </b>: <code>{title}</code>\n" 
        if gofile_links:
            text += "\n<b>🔰GoFile Link🔰 (Directly Leech)</b>\n"
            for i, link in enumerate(gofile_links, 1):
                text += f"<b>• {link}</b>\n"
              
        text += f"\n<b>🐬Stream Tape Link🐬\n {watch_url}</b> \n\n"
          
        if normal_links:
            text += "<b>🍿 All Cloud Links 🍿</b>\n"
            for i, link in enumerate(normal_links, 1):
                text += f"<b>{i}. {link}</b>\n"        

        text += f"\n<b><blockquote>Scraped from <a href='https://t.me/MrSagarbots'>SkymoviesHD</a></blockquote></b>"
        # Send to channel
        await client.send_message(
            chat_id=TARGET_CHANNEL,
            text=text,
            disable_web_page_preview=True
        )
        print(f"Posted new movie: {title}")
        
    except Exception as e:
        print(f"Error processing movie: {e}")

# Background monitoring task
async def monitor_new_movies(client: Client):
    print("🎥 Movie monitoring started...")
    state = load_processed_urls()
    processed_urls = set(state["processed_urls"])
    
    while True:
        try:
            print("🔍 Checking for new movies...")
            movies = await get_latest_movies()
            new_movies = [m for m in movies if m["url"] not in processed_urls]
            
            if new_movies:
                print(f"🎉 Found {len(new_movies)} new movies!")
                # Process in reverse order to send oldest first
                for movie in reversed(new_movies):
                    await process_and_send_movie(client, movie["url"])
                    processed_urls.add(movie["url"])
                    # Update state after each movie to prevent loss on crash
                    save_processed_urls(list(processed_urls))
                    await asyncio.sleep(10)  # Delay between processing
            else:
                print("🔄 No new movies found")
                
        except Exception as e:
            print(f"⚠️ Monitoring error: {e}")
            
        await asyncio.sleep(CHECK_INTERVAL)


# Command to start monitoring manually
@Client.on_message(filters.command("startmon") & filters.user(ADMIN_ID))
async def start_monitoring_cmd(client: Client, message: Message):
    asyncio.create_task(monitor_new_movies(client))
    await message.reply("✅ Movie monitoring started!")
