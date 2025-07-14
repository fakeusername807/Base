from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
from bs4 import BeautifulSoup

# ─── 1. Extract LinkMake URL ─────────────────────────────
async def get_linkmake_url(filmyfly_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(filmyfly_url, timeout=15) as r:
            html = await r.text()
    soup = BeautifulSoup(html, "html.parser")
    dlbtn = soup.find("div", class_="dlbtn")
    return dlbtn.a["href"] if dlbtn and dlbtn.a else None

# ─── 2. Extract filesdl.in/cloud links ──────────────────
async def get_filesdl_cloud_links(linkmake_url: str) -> list:
    async with aiohttp.ClientSession() as session:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with session.get(linkmake_url, headers=headers, timeout=15) as r:
            html = await r.text()
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for div in soup.find_all("div", class_="dlink"):
        a_tag = div.find("a")
        label = div.get_text(strip=True)
        if a_tag and a_tag["href"].startswith("http"):
            results.append({"label": label, "url": a_tag["href"]})
    return results

# ─── 3. Extract final download links from cloud ─────────
async def get_final_download_links(cloud_url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with session.get(cloud_url, headers=headers, timeout=15) as r:
            html = await r.text()
    soup = BeautifulSoup(html, "html.parser")

    title_div = soup.find("div", class_="title")
    title = title_div.text.strip() if title_div else "Unknown Title"

    links = []
    for a in soup.find_all("a", class_=lambda c: c and "button" in c):
        label = a.get_text(strip=True)
        href = a.get("href")
        if href and href.startswith("http"):
            links.append({"label": label, "url": href})

    return {"title": title, "links": links}

# ─── 4. /b Command that uses all above ──────────────────
@Client.on_message(filters.command("b", prefixes="/"))
async def filmyfly_bypass(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage:\n`/b <filmyfly.movie.page>`")

    movie_url = message.command[1]
    await message.reply_chat_action("typing")

    try:
        # Step 1: Get LinkMake URL
        linkmake_url = await get_linkmake_url(movie_url)
        if not linkmake_url:
            return await message.reply_text("❌ Failed to extract LinkMake URL.")

        # Step 2: Get Cloud links
        cloud_links = await get_filesdl_cloud_links(linkmake_url)
        if not cloud_links:
            return await message.reply_text("❌ No cloud links found on LinkMake page.")

        # Step 3: For each cloud link, get final download links
        final_output = []
        for item in cloud_links:
            cloud_url = item["url"]
            cloud_data = await get_final_download_links(cloud_url)
            cloud_title = cloud_data["title"]
            links = cloud_data["links"]

            section = f"<b>🎬 {cloud_title}</b>\n"
            for link in links:
                section += f"<b>{link['label']}</b>\n<code>{link['url']}</code>\n\n"
            final_output.append(section)

        # Send combined result
        if final_output:
            await message.reply_text("\n".join(final_output), disable_web_page_preview=True)
        else:
            await message.reply_text("❌ No final links extracted.")

    except Exception as e:
        await message.reply_text(f"❌ Error:\n<code>{str(e)}</code>")
