import aiohttp
import re
from bs4 import BeautifulSoup
from pyrogram import Client, filters 
async def extract_linkmake_view_url(page_url: str) -> str:
    """Extract linkmake.in/view URL from filmyfly.party page"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(page_url) as response:
                html = await response.text()
                match = re.search(
                    r'<div\s+class\s*=\s*["\']?dlbtn[^>]+href\s*=\s*["\'](https?://linkmake\.in/view/[^\s"\'<>]+)',
                    html,
                    re.IGNORECASE
                )
                return match.group(1) if match else ""
    except Exception:
        return ""

async def scrape_linkmake_downloads(linkmake_url: str):
    """Scrape download links from linkmake.in page"""
    result = {"title": "", "downloads": []}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(linkmake_url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract page title
                if title_tag := soup.find('title'):
                    result['title'] = title_tag.get_text(strip=True)
                
                # Find container with download links
                if container := soup.find('div', class_='container'):
                    # Extract file title
                    if file_title := container.find('div', class_='title'):
                        result['file_title'] = file_title.get_text(strip=True)
                    
                    # Extract all download buttons
                    buttons = container.find_all('a', class_=lambda x: x and x.startswith('button'))
                    
                    for button in buttons:
                        if href := button.get('href', '').strip():
                            result['downloads'].append({
                                "text": button.get_text(strip=True),
                                "url": href,
                                "type": "cloud" if "cloud" in href or "filesdl" in href else "other"
                            })
    except Exception:
        pass
    return result

async def get_filmyfly_cloud_urls(filmyfly_url: str):
    """Get all cloud download URLs from filmyfly.party page via linkmake.in"""
    # Step 1: Extract linkmake.in URL
    linkmake_url = await extract_linkmake_view_url(filmyfly_url)
    if not linkmake_url:
        return {"error": "No linkmake.in URL found"}
    
    # Step 2: Scrape download links from linkmake.in
    data = await scrape_linkmake_downloads(linkmake_url)
    
    # Filter cloud downloads
    cloud_downloads = [
        {"text": d["text"], "url": d["url"]}
        for d in data.get("downloads", [])
        if d.get("type") == "cloud"
    ]
    
    return {
        "title": data.get("title", ""),
        "file_title": data.get("file_title", ""),
        "cloud_downloads": cloud_downloads,
        "source_url": linkmake_url
    }





@Client.on_message(filters.command("filmyfly"))
async def handle_filmyfly(client, message):
    if len(message.command) < 2:
        return await message.reply("Please provide a filmyfly.party URL\nUsage: /filmyfly https://filmyfly.party/...")
    
    filmyfly_url = message.command[1]
    msg = await message.reply("Processing... Please wait")
    
    result = await get_filmyfly_cloud_urls(filmyfly_url)
    
    if "error" in result:
        return await msg.edit(result["error"])
    
    # Format response
    response = f"**Title:** `{result['title']}`\n"
    response += f"**File:** `{result.get('file_title', '')}`\n\n"
    response += "**Cloud Downloads:**\n"
    
    for i, download in enumerate(result["cloud_downloads"], 1):
        response += f"{i}. **{download['text']}**\n`{download['url']}`\n\n"
    
    response += f"_[Source Link]({result['source_url']})_"
    
    await msg.edit(
        text=response,
        disable_web_page_preview=True
    )

