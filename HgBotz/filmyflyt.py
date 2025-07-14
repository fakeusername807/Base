from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
from bs4 import BeautifulSoup

# Step 1: Extract first two links
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

# Step 2: Follow howblogs.xyz and extract all downloadable links
async def extract_download_links_from_howblogs(url: str) -> list:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=20) as resp:
                if resp.status != 200:
                    return [f"❌ Failed to load redirect page ({resp.status})"]
                html = await resp.text()

        soup = BeautifulSoup(html, "html.parser")
        links = []

        for a in soup.find_all("a", href=True):
            href = a['href'].strip()
            if any(domain in href for domain in ["gdlink.dev", "dgdrive", "hubdrive", "gdtot", "hubcloud", "filepress", "media.cm", "gofile.io"]):
                links.append(href)

        return links if links else ["❌ No valid GDrive-style links found on redirect page"]

    except Exception as e:
        return [f"❌ Error scraping redirect: {e}"]

# Pyrogram Command Handler
@Client.on_message(filters.command("skt") & filters.private)
async def skymovies_all_links(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage:\n/skt skymovieshd_url")

    url = message.command[1]
    await message.reply("🔍 Scraping watch and Google Drive redirect links...")

    # Step 1: scrape main page
    links = await scrape_first_two_links(url)
    if "error" in links:
        return await message.reply(links["error"])

    watch_link = links.get("WATCH ONLINE")
    gdrive_redirect = links.get("Google Drive Direct Links")

    # Step 2: follow the redirect and extract real links
    final_links = await extract_download_links_from_howblogs(gdrive_redirect)

    # Format the message
    text = "✅ <b>SkymoviesHD Links</b>\n\n"
    text += f"<b>🎬 Watch Online:</b> <a href='{watch_link}'>Click Here</a>\n"
    text += f"<b>📦 Google Drive Redirect:</b> <a href='{gdrive_redirect}'>Click Here</a>\n\n"
    text += "<b>🔗 Final Download Links:</b>\n"

    for idx, link in enumerate(final_links, start=1):
        text += f"{idx}. <a href='{link}'>Link {idx}</a>\n"

    await message.reply(text, disable_web_page_preview=True)
