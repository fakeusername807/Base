import re
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
@Client.on_message(filters.command("sky") & filters.private)
async def skymovies_full_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /skt skymovieshd_url")

    url = message.command[1]
    await message.reply("🔍 Scraping all links, please wait...")
    
    pattern = r'.*/(.*)\.html$'
    match = re.match(pattern, url) 
    if match:
        title = match.group(1)

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
    text += f"<b>🐬Stream Tape Link🐬 \n {watch_url} \n\n</b>"
    text += "<b><blockquote>Cloud Urls 💥</blockquote></b>\n"
    for i, link in enumerate(normal_links, 1):
        text += f"<b>{i}. {link}</b>\n"

    if gofile_links:
        text += "\n<b><blockquote>🔰GoFile Link🔰</blockquote></b>\n"
        for i, link in enumerate(gofile_links, 1):
            text += f"<b>• {link}</b>\n"

    await message.reply(text,  disable_web_page_preview=True)



# Add these global variables at the top of your script
LAST_CHECKED_MOVIES = []
MONITOR_INTERVAL = 1800  # 30 minutes in seconds
TARGET_CHANNEL = "-1002615965065"  # Change to your channel
admin = "6359874284" 
# Add this function to check for new movies
async def get_latest_movies() -> List[Dict[str, str]]:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BASE_URL, timeout=20) as resp:
                if resp.status != 200:
                    return []
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        fmvideo_divs = soup.find_all("div", class_="Fmvideo")
        
        movies = []
        for div in fmvideo_divs[:10]:  # Check latest 10 movies
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

# Add this background task
async def monitor_new_movies(client: Client):
    global LAST_CHECKED_MOVIES
    
    while True:
        try:
            current_movies = await get_latest_movies()
            
            if not LAST_CHECKED_MOVIES:
                LAST_CHECKED_MOVIES = current_movies
                await asyncio.sleep(MONITOR_INTERVAL)
                continue
                
            # Find new movies that weren't in last check
            new_movies = [
                movie for movie in current_movies 
                if movie not in LAST_CHECKED_MOVIES
            ]
            
            # Process and send new movies
            for movie in new_movies:
                try:
                    # Use the same logic as your /sky command
                    url = movie["url"]
                    pattern = r'.*/(.*)\.html$'
                    match = re.match(pattern, url) 
                    title = match.group(1) if match else movie["title"]
                    
                    data = await scrape_first_three_links(url)
                    if "error" in data:
                        continue
                        
                    watch_url = data.get("WATCH ONLINE")
                    gdrive_redirect = data.get("Google Drive Direct Links")
                    server01_redirect = data.get("SERVER 01")

                    gdrive_links = await extract_external_links_gdrive(gdrive_redirect)
                    server01_links = await extract_external_links_gdrive(server01_redirect)

                    gofile_links = []
                    normal_links = []

                    for link in gdrive_links + server01_links:
                        if "gofile.io" in link:
                            gofile_links.append(link)
                        
                    for link in gdrive_links:
                        if link.startswith("http"):
                            normal_links.append(link)

                    text = " <b>🎬 New Movie Added! ✅</b>\n\n"
                    text += f" <b>Title</b> = <code>{title}</code>\n\n" 
                    text += f"<b>🐬Stream Tape Link🐬 \n {watch_url} \n\n</b>"
                    text += "<b><blockquote>Cloud Urls 💥</blockquote></b>\n"
                    for i, link in enumerate(normal_links, 1):
                        text += f"<b>{i}. {link}</b>\n"

                    if gofile_links:
                        text += "\n<b><blockquote>🔰GoFile Link🔰</blockquote></b>\n"
                        for i, link in enumerate(gofile_links, 1):
                            text += f"<b>• {link}</b>\n"

                    await client.send_message(
                        chat_id=TARGET_CHANNEL,
                        text=text,
                        disable_web_page_preview=True
                    )
                    
                except Exception as e:
                    print(f"Error processing {movie['title']}: {e}")
            
            LAST_CHECKED_MOVIES = current_movies
            
        except Exception as e:
            print(f"Monitoring error: {e}")
        
        await asyncio.sleep(MONITOR_INTERVAL)

# Add this handler to start monitoring when bot starts
@Client.on_message(filters.command("startmonitor") & filters.user(admin))  # Only for admins
async def start_monitoring(client: Client, message: Message):
    await message.reply("🔄 Starting movie monitoring...")
    asyncio.create_task(monitor_new_movies(client))

