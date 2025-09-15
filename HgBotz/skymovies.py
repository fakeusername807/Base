# skymovieshd.py
import os, re, aiohttp, json, asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from bs4 import BeautifulSoup

# ===========================
# Step 1: Scrape first 3 links
# ===========================
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
            "WATCH ONLINE": a_tags[0].get("href", "").strip(),
            "Google Drive Direct Links": a_tags[1].get("href", "").strip(),
            "SERVER 01": a_tags[2].get("href", "").strip(),
        }
        return result

    except Exception as e:
        return {"error": f"❌ Exception in main page: {e}"}

# ===========================
# Step 2: Extract external links
# ===========================
async def extract_external_links(url: str) -> list:
    if not url:
        return []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=20) as response:
                if response.status != 200:
                    return []
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                return [a["href"].strip() for a in soup.find_all("a", rel="external") if a.has_attr("href")]
    except Exception:
        return []

# ===========================
# CONFIG
# ===========================
BASE_URL = "https://skymovieshd.credit/"
STATE_FILE = "skymovies_state.json"
TARGET_CHANNEL = -1002557688309   # full post here
GOFILE_CHANNEL = -1002996723284   # only /leech gofile link
ADMIN_ID = 7965786027
CHECK_INTERVAL = 420  # seconds

# ===========================
# Utility: pick last gofile link
# ===========================
def pick_last_gofile(links: list) -> str:
    gofiles = [l.strip() for l in links if l and "gofile.io" in l]
    return gofiles[-1] if gofiles else ""

# ===========================
# Format target channel post
# ===========================
def format_target_post(title: str, watch_url: str, all_links: list) -> str:
    gofile_links = [l for l in all_links if "gofile.io" in l]
    normal_links = [l for l in all_links if "gofile.io" not in l]

    text = "<b>🎬 New Post Just Dropped! ✅</b>\n\n"
    text += f"<b>📌 Title </b>: <code>{title}</code>\n" 

    if gofile_links:
        text += "\n<b><blockquote>🔰 GoFile Link 🔰 (Directly Leech)</blockquote></b>\n"
        for i, link in enumerate(gofile_links, 1):
            text += f"<b>• {link}</b>\n"
          
    if watch_url:
        text += f"\n<b><blockquote>🐬 Stream Tape Link 🐬</blockquote>\n {watch_url}</b>\n"
      
    if normal_links:
        text += "\n<b><blockquote>🍿 All Cloud Links 🍿</blockquote></b>\n"
        for i, link in enumerate(normal_links, 1):
            text += f"<b>{i}. {link}</b>\n"        

    text += f"\n<b><blockquote>Scraped from <a href='https://t.me/MrSagarbots'>SkymoviesHD</a></blockquote></b>"
    return text

# ===========================
# Manual command
# ===========================
@Client.on_message(filters.command("sky") & filters.all)
async def skymovies_full_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /sky <skymovieshd_url>")

    url = message.command[1]
    M = await message.reply("🔍 scraping...")

    pattern = r'.*/(.*)\.html$'
    match = re.match(pattern, url) 
    title = match.group(1).replace("-", " ") if match else "Unknown Title"

    data = await scrape_first_three_links(url)
    if "error" in data:
        return await M.edit_text(data["error"])

    watch_url = data.get("WATCH ONLINE", "")
    gdrive_links = await extract_external_links(data.get("Google Drive Direct Links", ""))
    server01_links = await extract_external_links(data.get("SERVER 01", ""))

    all_links = gdrive_links + server01_links
    gofile_link = pick_last_gofile(all_links)

    # ✅ Send formatted text post to target channel
    text = format_target_post(title, watch_url, all_links)
    try:
        await client.send_message(
            chat_id=TARGET_CHANNEL,
            text=text,
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"❌ Failed to post to TARGET_CHANNEL: {e}")

    # ✅ Send only /leech GoFile link to GoFile channel
    if gofile_link:
        try:
            await client.send_message(chat_id=GOFILE_CHANNEL, text=f"/leech {gofile_link}")
        except Exception as e:
            print(f"❌ Failed to post gofile to GOFILE_CHANNEL: {e}")

    await M.edit_text("✅ Posted to both channels")

# ===========================
# Auto Monitor
# ===========================
def load_processed_urls():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"processed_urls": []}

def save_processed_urls(urls):
    with open(STATE_FILE, "w") as f:
        json.dump({"processed_urls": urls}, f)

def clean_title(title: str) -> str:
    # Remove [size], (size), {size} patterns like [1.7GB], (850MB), {2.3 GB}
    title = re.sub(r'[\[\(\{]\s*\d+(\.\d+)?\s*(GB|MB)\s*[\]\)\}]', '', title, flags=re.IGNORECASE)
    # Strip extra spaces
    title = re.sub(r'\s+', ' ', title).strip()
    # Always add .mkv
    if not title.lower().endswith(".mkv"):
        title = f"{title}.mkv"
    return title


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
        for div in fmvideo_divs[:20]:
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

async def process_and_send_movie(client: Client, movie_url: str):
    try:
        # Title
        pattern = r'.*/(.*)\.html$'
        match = re.match(pattern, movie_url) 
        title = match.group(1).replace("-", " ") if match else "Unknown Title"

        # Scrape
        data = await scrape_first_three_links(movie_url)
        if "error" in data:
            return

        watch_url = data.get("WATCH ONLINE", "")
        gdrive_links = await extract_external_links(data.get("Google Drive Direct Links", ""))
        server01_links = await extract_external_links(data.get("SERVER 01", ""))
        all_links = gdrive_links + server01_links
        gofile_link = pick_last_gofile(all_links)

        # ✅ Full formatted post in target channel
        text = format_target_post(title, watch_url, all_links)
        await client.send_message(
            chat_id=TARGET_CHANNEL,
            text=text,
            disable_web_page_preview=True
        )
        
        # Add .mkv extension to title
        file_title = clean_title(title)

        # ✅ Only gofile in gofile channel
        if gofile_link:
            await client.send_message(chat_id=GOFILE_CHANNEL, text=f"/leech {gofile_link} -n {file_title}")

    except Exception as e:
        print(f"⚠️ Error processing movie: {e}")

async def monitor_new_movies(client: Client):
    state = load_processed_urls()
    processed_urls = set(state["processed_urls"])
    while True:
        try:
            movies = await get_latest_movies()
            new_movies = [m for m in movies if m["url"] not in processed_urls]
            for movie in reversed(new_movies):
                await process_and_send_movie(client, movie["url"])
                processed_urls.add(movie["url"])
                save_processed_urls(list(processed_urls))
                await asyncio.sleep(10)
        except Exception as e:
            print(f"⚠️ Monitoring error: {e}")
        await asyncio.sleep(CHECK_INTERVAL)

@Client.on_message(filters.command("startmon") & filters.user(ADMIN_ID))
async def start_monitoring_cmd(client: Client, message: Message):
    asyncio.create_task(monitor_new_movies(client))
    await message.reply("✅ Movie monitoring started!")
