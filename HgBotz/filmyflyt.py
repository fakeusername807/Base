import os
from pyrogram import Client, filters
from pyrogram.types import Message
import aiohttp
from bs4 import BeautifulSoup
import html
# ─── 1. Extract LinkMake URL ─────────────────────────────
async def get_linkmake_url(filmyfly_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(filmyfly_url, timeout=15) as r:
            html = await r.text()
    soup = BeautifulSoup(html, "html.parser")
    dlbtn = soup.find("div", class_="dlbtn")
    return dlbtn.a["href"] if dlbtn and dlbtn.a else None


async def extract_new1_links_with_labels(linkmake_url: str) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(linkmake_url, timeout=20) as r:
            html = await r.text()

    soup = BeautifulSoup(html, "html.parser")
    results = []

    # ✅ This finds ALL <a href="https://new1.filesdl.in/..."> inside any <div class="dlink dl">
    for div in soup.find_all("div", class_="dlink dl"):
        a_tag = div.find("a", href=True)
        label_tag = div.find("div", class_="dll")

        if a_tag and "new1.filesdl.in" in a_tag["href"]:
            url = a_tag["href"].strip()
            label = label_tag.get_text(strip=True) if label_tag else "No Label"
            results.append({"label": label, "url": url})

    return results
# ─── 2. Extract filesdl.in/cloud links ──────────────────
async def extract_new1_links(linkmake_url: str) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(linkmake_url, timeout=20) as r:
            html = await r.text()

    soup = BeautifulSoup(html, "html.parser")
    all_links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "new1.filesdl.in" in href:
            all_links.append(href)

    return all_links

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
        return await message.reply_text("❌ Usage:\n/b filmyfly.movie.page")

    movie_url = message.command[1]
    await message.reply_text(text="process") 

    try:
        # Step 1: Get LinkMake URL
        linkmake_url = await get_linkmake_url(movie_url)
        if not linkmake_url:
            return await message.reply_text("❌ Failed to extract LinkMake URL.")

        # Step 2: Get Cloud links
        cloud_links = await extract_new1_links(linkmake_url)
        if not cloud_links:
            return await message.reply_text(f"{linkmake_url} ❌ No cloud links found on LinkMake page.")

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






async def extract_new1_links(url: str) -> list:
    """Extract new1.filesdl.in links with their labels from linkmake.in page"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                
                links = []
                containers = soup.find_all("div", class_="dlink dl")
                
                for container in containers:
                    link_tag = container.find("a", title="new1.filesdl")
                    if not link_tag:
                        continue
                    
                    href = link_tag.get("href")
                    label_div = link_tag.find("div", class_="dll")
                    label = label_div.get_text(strip=True) if label_div else "Download Link"
                    
                    links.append((label, href))
                
                return links if links else None
                
    except Exception as e:
        print(f"Scraping error: {e}")
        return None

@Client.on_message(filters.command("filesdl", prefixes="/"))
async def get_filesdl_links(client, message: Message):
    # Extract URL from command
    if len(message.command) < 2:
        return await message.reply_text("**Usage:**\n`/filesdl https://linkmake.in/view/...`")
    
    url = message.command[1].strip()
    if not url.startswith("http"):
        url = "https://" + url
    
    # Show processing status
    processing_msg = await message.reply_text("🔍 __Scraping linkmake.in page...__")
    
    # Extract links
    links = await extract_new1_links(url)
    
    if not links:
        await processing_msg.delete()
        return await message.reply_text("❌ No new1.filesdl.in links found or invalid URL.")
    
    # Prepare response
    response_text = f"**✅ Found {len(links)} Download Links:**\n\n"
    keyboard = []
    
    for i, (label, url) in enumerate(links, 1):
        response_text += f"{i}. **{label}**\n`{url}`\n\n"
        keyboard.append([InlineKeyboardButton(label, url=url)])
    
    # Send results with inline buttons
    await processing_msg.delete()
    await message.reply_text(
        response_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )
