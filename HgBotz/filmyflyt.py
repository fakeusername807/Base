from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
from bs4 import BeautifulSoup

# Async function to scrape only first 2 links
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
        return {"error": f"❌ Exception: {e}"}

# Pyrogram command handler
@Client.on_message(filters.command("sky") & filters.private)
async def skymovies_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /skt skymovieshd_url")

    url = message.command[1]
    await message.reply("🔍 Scraping Watch & GDrive links...")

    links = await scrape_first_two_links(url)

    if "error" in links:
        return await message.reply(links["error"])

    text = "✅ <b>Links Extracted:</b>\n\n"
    for label, link in links.items():
        text += f"<b>{label}:</b> <a href='{link}'>Click Here</a>\n"

    await message.reply(text, disable_web_page_preview=True)
