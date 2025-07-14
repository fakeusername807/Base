from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
from bs4 import BeautifulSoup

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
        elif link.startswith("http"):
            normal_links.append(link)

    # Step 4: Format output
    text = " <b>🎬 New Post Just Dropped! ✅</b>\n\n"
    
    text += "<b>Cloud Urls 💥</b>\n"
    for i, link in enumerate(normal_links, 1):
        text += f"<b>{i}. {link}</b>\n"

    if gofile_links:
        text += "\n<b>🔰GoFile Link🔰 </b>\n"
        for i, link in enumerate(gofile_links, 1):
            text += f"<b>• {link}</b>\n"

    await message.reply(text,  disable_web_page_preview=True)
