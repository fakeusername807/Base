import re
from pyrogram import Client, filters
from pyrogram.types import Message
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

@Client.on_message(filters.command("ultraplay") & filters.private)
async def pvt_nf_cmd(client, message: Message):
    await message.reply_text(
        text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>",
        disable_web_page_preview=False
    )

@Client.on_message(filters.command("ultraplay") & filters.group & force_sub_filter())
async def ultraplay_simple(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
    if len(message.command) < 2:
        return await message.reply("❌ Usage: /ultraplay <Ultraplay URL>", quote=True)

    url = message.command[1].strip()

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_selector("h1.content-title")  # ensures JS-rendered title exists
            html = await page.content()
            await browser.close()
    except Exception as e:
        return await message.reply(f"❌ Failed to load page: {e}", quote=True)

    soup = BeautifulSoup(html, "html.parser")

    # Poster URL
    poster_tag = soup.select_one(".content-image img")
    poster_url = poster_tag["src"] if poster_tag else None

    # Title
    title_tag = soup.select_one("h1.content-title")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown"

    # Year
    year = "Unknown"
    for p_tag in soup.select(".content-sub-detail p"):
        text = p_tag.get_text(strip=True)
        match = re.search(r"\b(\d{4})\b", text)
        if match:
            year = match.group(1)
            break

    # Build and send response
    if poster_url:
        await message.reply_text(f"**Ultraplay Poster: {poster_url}\n\n{title} ({year})**\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>", quote=True)
    else:
        await message.reply_text(f"{title} ({year})\n❌ Poster not found", quote=True)
