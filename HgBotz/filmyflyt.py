from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
from bs4 import BeautifulSoup

# Scrape WATCH ONLINE and Google Drive Redirect
async def scrape_first_two_links(page_url: str) -> dict:
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
        if len(a_tags) < 2:
            return {"error": "❌ Less than 2 links found"}

        result = {
            a_tags[0].text.strip() or "WATCH ONLINE": a_tags[0].get("href", "").strip(),
            a_tags[1].text.strip() or "Google Drive Direct Links": a_tags[1].get("href", "").strip()
        }

        return result

    except Exception as e:
        return {"error": f"❌ Exception in main page: {e}"}

# Your provided GDrive redirect parser
async def extract_external_links_gdrive(url: str) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=20) as response:
                if response.status != 200:
                    return [f"❌ Failed to fetch GDrive redirect page: {response.status}"]

                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")

                links = [
                    a["href"].strip()
                    for a in soup.find_all("a", rel="external")
                    if a.has_attr("href")
                ]

                return links if links else ["❌ No external links found on redirect page."]

    except Exception as e:
        return [f"❌ Exception while scraping GDrive redirect page: {e}"]

# Pyrogram command handler
@Client.on_message(filters.command("skt") & filters.private)
async def skymovies_gdrive_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /skt skymovieshd_url")

    url = message.command[1]
    await message.reply("🔍 Scraping page, please wait...")

    # Step 1: Get watch & GDrive redirect links
    data = await scrape_first_two_links(url)
    if "error" in data:
        return await message.reply(data["error"])

    watch_url = data.get("WATCH ONLINE")
    gdrive_redirect_url = data.get("Google Drive Direct Links")

    # Step 2: Extract final links from GDrive redirect page
    gdrive_links = await extract_external_links_gdrive(gdrive_redirect_url)

    # Step 3: Compose reply
    text = "✅ <b>SkymoviesHD Extracted Links</b>\n\n"
    text += f"🎬 <b>Watch Online:</b> <a href='{watch_url}'>Click Here</a>\n"
    text += f"📁 <b>GDrive Redirect Page:</b> <a href='{gdrive_redirect_url}'>Click Here</a>\n\n"
    text += "<b>📦 Final Download Links:</b>\n"

    for i, link in enumerate(gdrive_links, start=1):
        text += f"{i}. <a href='{link}'>Link {i}</a>\n"

    await message.reply(text,  disable_web_page_preview=True)
