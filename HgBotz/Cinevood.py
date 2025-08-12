import aiohttp
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message

async def extract_oxxfile_links(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch URL. Status: {response.status}")
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else "No title found"

    links = []
    current_h6 = ""

    for tag in soup.find_all(["h6", "a"]):
        if tag.name == "h6":
            current_h6 = tag.get_text(strip=True)
        elif tag.name == "a" and "maxbutton-oxxfile" in tag.get("class", []):
            href = tag.get("href", "").strip()
            if href and current_h6:
                links.append({"title": current_h6, "url": href})
                current_h6 = ""

    return {"title": title, "links": links}



@Client.on_message(filters.command("cinevood") & filters.private)
async def cinvood_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /cinvood url")

    url = message.command[1]
    reply = await message.reply("🔍 Extracting links...")

    try:
        data = await extract_oxxfile_links(url)

        if not data["links"]:
            return await reply.edit("⚠️ No OxxFile links found.")

        result = f"📄 <b>{data['title']}</b>\n\n"
        for i, item in enumerate(data["links"], 1):
            result += f"{i}. <b>{item['title']}</b>\n🔗 <code>{item['url']}</code>\n\n"

        await reply.edit(result)

    except Exception as e:
        await reply.edit(f"❌ Error: {str(e)}")
