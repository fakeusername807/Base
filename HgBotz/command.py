import requests
from pyrogram import Client, filters, errors, types, enums 
from config import HgBotz
import os, asyncio, re, time, sys, random, html
from .database import total_user, getid, delete, insert, get_all_users, authorize_chat, unauthorize_chat, is_chat_authorized, get_all_authorized_chats
from pyrogram.errors import *
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from Script import script
import aiohttp
from bs4 import BeautifulSoup
from pyrogram import Client, filters
import json
from urllib.parse import unquote, parse_qs, urlparse
from PIL import Image
from io import BytesIO


# Step 1: Get filename + PHP URL from HubCloud
async def extract_filename_and_php_link(hubcloud_url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(hubcloud_url) as response:
            if response.status != 200:
                return {"error": f"Failed to fetch HubCloud page. Status: {response.status}"}
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")

    # File name
    file_name_div = soup.find("div", class_="card-header text-white bg-primary mb-3")
    file_name = file_name_div.text.strip() if file_name_div else None

    # PHP download link
    php_link_tag = soup.select_one("div.vd a#download")
    php_url = php_link_tag['href'] if php_link_tag else None

    return {
        "file_name": file_name,
        "php_url": php_url
    }


# Step 2: Get download links from PHP page
async def extract_links_from_php_page(php_url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(php_url) as resp:
            if resp.status != 200:
                return {"error": "Failed to load PHP page."}
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")
    pixel_link, fsl_link = None, None

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "pixeldrain" in href and "api/file" in href:
            pixel_link = href
        elif "cdn.cdn3bot.xyz" in href:
            fsl_link = href

    return {
        "pixel_server": pixel_link,
        "fsl_server": fsl_link
    }


# Step 3: Pyrogram command handler
@Client.on_message(filters.command("hubcloud") & filters.reply)
async def handle_hubcloud_all(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.text.startswith("http"):
        return await message.reply_text("❌ Reply to a HubCloud page URL (e.g. https://hubcloud.one/drive/...).")

    url = reply.text.strip()
    await message.reply_text("🔍 Fetching file info and download links...")

    base_data = await extract_filename_and_php_link(url)
    if "error" in base_data or not base_data["php_url"]:
        return await message.reply_text("❌ Could not extract PHP link from page.")

    file_name = base_data["file_name"] or "Unknown File"
    php_url = base_data["php_url"]

    # Step 2: Get Pixel + FSL
    dl_links = await extract_links_from_php_page(php_url)

    if "error" in dl_links:
        return await message.reply_text("❌ Failed to extract download links.")

    pixel = dl_links.get("pixel_server")
    fsl = dl_links.get("fsl_server")

    # Final output
    msg = f"<b>📁 File Name:</b> <code>{file_name}</code>\n"
    msg += f"<b>🔗 PHP Page:</b> <a href='{php_url}'>Open Link</a>\n\n"
    msg += f"📥 <b>PixelServer</b>: <a href='{pixel}'>Click Here</a>\n" if pixel else "❌ PixelServer not found.\n"
    msg += f"📥 <b>FSL Server</b>: <a href='{fsl}'>Click Here</a>" if fsl else "❌ FSL Server not found."

    await message.reply_text(msg,  disable_web_page_preview=True)

#-----------------------INLINE BUTTONS - - - - - - - - - - - - - - - 
buttons = [[
        InlineKeyboardButton('✇ Uᴘᴅᴀᴛᴇs ✇', url="https://t.me/HGBOTZ"),
        InlineKeyboardButton('🦋 about', callback_data='about')
    ],[
        InlineKeyboardButton('𝙷𝚎𝚕𝚙 ‼️', callback_data='help')
    ]]

group_buttons = [[InlineKeyboardButton('✇ Click To Start Me ✇', url="http://t.me/Reaction_99bot?start=True")
               ],[
                  InlineKeyboardButton('✇ Uᴘᴅᴀᴛᴇs ✇', url="https://t.me/HGBOTZ")
                ]] 


back_button = [[
                 InlineKeyboardButton('sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/HGBOTZ_support'),
                 InlineKeyboardButton('ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://telegram.me/hgbotz')
              ],[
                 InlineKeyboardButton('🔙 back', callback_data='back')
              ]]



help_buttons = [[        
        InlineKeyboardButton('🙂 𝐎𝐖𝐍𝐄𝐑', url='https://t.me/Harshit_contact_bot'), 
        InlineKeyboardButton('BACK 🔙', callback_data='back')
        ]]

about_buttons = [[
        InlineKeyboardButton('🙂 𝐎𝐖𝐍𝐄𝐑', url='https://t.me/Harshit_contact_bot')
        ],[
        InlineKeyboardButton('𝙷𝚎𝚕𝚙 ‼️', callback_data='help'), 
        InlineKeyboardButton('🦋 𝙷𝙾𝙼𝙴', callback_data='back')
        ],[
        InlineKeyboardButton('📜 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/HGBOTZ_support'),
        InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://telegram.me/hgbotz')
        ]]


update_button = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("💥 𝚄𝚙𝚍𝚊𝚝𝚎 𝙲𝚑𝚊𝚗𝚗𝚎𝚕", url="https://t.me/hgbotz")]
    ]
)



dump_chat = -1002637710224
# 🧩 Environment Variables
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "HGBOTZ")  # e.g. @YourChannelUsername or -100xxxxxxxxxx
FSUB_TEXT = os.getenv("FSUB_TEXT", "<b>Hey {} , Seems Like You Haven't Joined Our Channel(s).\n Please Join Below & Then Try Again .</b>")  # Image to show when not subscribed

# ✅ Main Fsub Check Function
async def handle_fsub(client: Client, user_id: int):
    try:
        member = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        if member.status in ["kicked", "banned"]:
            return "banned", None
        return "ok", None

    except UserNotParticipant:
        try:
            invite_link = await client.export_chat_invite_link(FORCE_SUB_CHANNEL)
        except ChatAdminRequired:
            invite_link = f"https://t.me/{FORCE_SUB_CHANNEL.strip('@')}"
        return "not_subscribed", invite_link

    except Exception as e:
        return "error", str(e)

# ✅ Inline Buttons for Join + I Joined
def fsub_markup(invite_link: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Updates Channel", url=invite_link)]
        ])

# ✅ Force Sub Filter (Reusable in all commands)
def force_sub_filter():
    async def func(_, __, message):
        

        client = message._client  # ✅ Get actual Client instance
        user_id = message.from_user.id
        status, data = await handle_fsub(client, user_id)

        if status == "ok":
            return True
        elif status == "not_subscribed":
            await message.reply_text(
                text=FSUB_TEXT.format(message.from_user.mention()),
                reply_markup=fsub_markup(data)
            )
        elif status == "banned":
            await message.reply("🚫 You are banned from using this bot.")
        else:
            await message.reply(f"⚠️ Error: {data}")
        return False

    return filters.create(func)



@Client.on_message(filters.command("auth") & filters.user(HgBotz.ADMIN))
async def auth_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Provide chat_id to authorize.\nUsage: `/auth -1001234567890`")
    try:
        chat_id = int(message.command[1])
        await authorize_chat(chat_id)
        await message.reply(f"✅ Chat `{chat_id}` has been authorized.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@Client.on_message(filters.command("unauth") & filters.user(HgBotz.ADMIN))
async def unauth_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Provide chat_id to unauthorize.\nUsage: `/unauth -1001234567890`")
    try:
        chat_id = int(message.command[1])
        await unauthorize_chat(chat_id)
        await message.reply(f"🚫 Chat `{chat_id}` has been unauthorized.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@Client.on_message(filters.command("auth_chat") & filters.user(HgBotz.ADMIN))
async def list_auth_chats(client, message):
    auth_chats = await get_all_authorized_chats()
    text = "**🔐 Authorized Chats:**\n"
    async for chat in auth_chats:
        text += f"`{chat['_id']}`\n"
    await message.reply(text if text.strip() != "**🔐 Authorized Chats:**" else "🚫 No authorized chats found.")



#-----------------------SEARCH FUNCTION - - - - - - - - - - - - - - - 
@Client.on_message(filters.command("search") & filters.private)
async def pvt_search_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("search") & filters.group & force_sub_filter())
async def search_handler(client, message: Message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    
    if len(message.command) < 2:
        return await message.reply_text(text="Usage: `/search movie name`")
    
    query = "+".join(message.command[1:])

    platforms = [
        ("Prime", "prime"),
        ("Airtel", "airtel"),
        ("ZEE5", "zee5"),
        ("Sony LIV", "sony"),
        ("MX Player", "mx"), 
        ("Sun NXT", "sun"),
        ("Lionsgate Play", "lionsgate"),
        ("Altt", "altt"), 
        ("Hoichoi", "hoichoi"),
        ("ShemarooMe", "shemaroo"),
        ("Eros Now", "eros"),
        ("Hungama", "hungama"),
        ("ManoramaMax", "manorama"),
        ("Aha", "aha"),
        ("Chaupal", "chaupal"),
        ("Ultra", "ultra"),
        ("EPICon", "epicon"),
        ("Docubay", "docubay"),
        ("Playflix", "playflix"),
        ("K-Drama Stage", "k-drama"),
        ("Kanccha Lanka", "kanccha"),
        ("Namma Flix", "namma"),
        ("Klikk", "klikk"),
        ("Raj Digital", "raj"),
        ("Shorts TV", "shorts"),
        ("Dollywood Play", "dollywood")       
      ]

    # Create rows of 3 buttons
    buttons = []
    row = []
    for name, key in platforms:
        row.append(InlineKeyboardButton(name, callback_data=f"search_{key}_{query}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    await message.reply_text(text=f"🔍 Choose a platform Where your query available to search:\n<code>{query.replace('+', ' ')}</code>",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex(r"^search_(\w+)_(.+)$"))
async def search_callback(client, query: CallbackQuery):
    platform, search_term = query.matches[0].group(1), query.matches[0].group(2)
    AIRTEL_URL = f"https://hgbots-hgbotz-s-projects.vercel.app/poster/ott.php?query={search_term}" 
    urls = {
        "prime": f"https://hgbots-hgbotz-s-projects.vercel.app/poster/prime.php?query={search_term}",
        "hotstar": AIRTEL_URL,
        "airtel": AIRTEL_URL,
        "sony": AIRTEL_URL,                                              
        "zee5": f"https://hgbots-hgbotz-s-projects.vercel.app/poster/zee.php?query={search_term}",
        "altt": AIRTEL_URL,
    "sun": AIRTEL_URL,                                              
    "lionsgate": AIRTEL_URL,
    "hoichoi": AIRTEL_URL,                                               
    "shemaroo": AIRTEL_URL,
    "eros": AIRTEL_URL,                                              
    "hungama": AIRTEL_URL,
    "manorama": AIRTEL_URL,                                               
    "aha": AIRTEL_URL,
    "chaupal": AIRTEL_URL,                                             
    "ultra": AIRTEL_URL,
    "epicon": AIRTEL_URL,                                              
    "docubay": AIRTEL_URL,
    "playflix": AIRTEL_URL,                                              
    "k-drama": AIRTEL_URL,
    "kanccha": AIRTEL_URL,                                               
    "namma": AIRTEL_URL,
    "klikk": AIRTEL_URL,                                       
    "raj": AIRTEL_URL,
    "shorts": AIRTEL_URL,                                               
    "dollywood": AIRTEL_URL,
    "mx": AIRTEL_URL, 
    }

    url = urls.get(platform)
    if not url:
        return await query.answer("Unknown platform")

    await query.message.edit_text(
        f"🔗 <b>Search Result for:</b> <code>{search_term.replace('+', ' ')}</code>\n\n<a href='{url}'>Click Here And Copy Your Content Url</a>",
        disable_web_page_preview=True
    )
    await query.answer()



#-----------------------IMGBB UPLOAD FUNCTION - - - - - - - - - - - - - - - 
# Get your free API key from https://api.imgbb.com/
IMG_BB_API_KEY = "3f9544c78f25c9ad94ab949cd2673b00"  # Replace with your actual key

async def upload_to_imgbb(image_url: str, custom_word: str = "image") -> str:
    """Upload image to ImgBB and return URL with custom word"""
    try:
        async with aiohttp.ClientSession() as session:
            # Prepare form data with custom parameters
            form = aiohttp.FormData()
            form.add_field('image', image_url)
            form.add_field('format', 'jpg')  # Force JPEG output
            form.add_field('name', 'HGBOTZ')  # Set custom word for URL
            
            # Upload to ImgBB
            async with session.post(
                "https://api.imgbb.com/1/upload",
                params={'key': IMG_BB_API_KEY},
                data=form
            ) as resp:
                data = await resp.json()
                
                # Process successful response
                if resp.status == 200 and data.get('success'):
                    # Get direct image URL
                    direct_url = data['data']['image']['url']
                    
                    # Extract image ID and build custom URL
                    parts = direct_url.split('/')
                    if len(parts) > 4:
                        # Get the image ID (second last path segment)
                        image_id = parts[-2]
                        # Construct new URL with custom word
                        return f"https://i.ibb.co/{image_id}/HGBOTZ.jpg"
                    
                return image_url  # Fallback to original URL on failure
                
    except Exception as e:
        print(f"ImgBB Upload Error: {e}")
        return image_url



#-----------------------Jpg Png To stkr FUNCTION - - - - - - - - - - - - - - - 
async def download_image(url: str) -> BytesIO:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return BytesIO(await resp.read())
            else:
                raise Exception(f"Failed to download image. Status code: {resp.status}")

@Client.on_message(filters.command("stkar") & filters.group & force_sub_filter())
async def sticker_cmd(client, message: Message):
    chat_id = message.chat.id

    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")

    try:
        reply = message.reply_to_message

        # ✅ Reply to image
        if reply and reply.photo:
            photo = await reply.download()
            img = Image.open(photo).convert("RGBA")

        # ✅ Image URL in command
        elif len(message.command) >= 2:
            url = message.command[1]
            img_data = await download_image(url)
            img = Image.open(img_data).convert("RGBA")

        else:
            return await message.reply("🔗 Please send an image URL or reply to an image.\nExample: `/stkar https://example.com/img.jpg`")

        # 🔄 Convert to WebP
        output = BytesIO()
        output.name = "sticker.webp"
        img.thumbnail((512, 512))
        img.save(output, "WEBP")
        output.seek(0)

        await message.reply_sticker(sticker=output)

    except Exception as e:
        await message.reply(f"❌ Failed to create sticker:\n`{e}`")
#-----------------------BMS EXTRACT FUNCTION - - - - - - - - - - - - - - - 

API_KEY = "fb85462f11c8c1e571b32fb8c739f71263a9bc8f"
SEARCH_ENDPOINT = "https://google.serper.dev/images"

def get_google_poster(query):
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }
    data = { "q": query }

    try:
        res = requests.post(SEARCH_ENDPOINT, headers=headers, json=data)
        res.raise_for_status()
        results = res.json()

        images = results.get("images", [])
        for img in images:
            if "bmscdn.com" in img["imageUrl"] or "imgsrv.crunchyroll.com" in img["imageUrl"]:  # Optional: prioritize BookMyShow
                return img["imageUrl"]
        return images[0]["imageUrl"] if images else None
    except Exception as e:
        print("Image fetch error:", e)
        return None

# 🚀 Telegram /bms command
@Client.on_message(filters.command("bms") & filters.private)
async def pvt_bms_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("bms") & filters.group & force_sub_filter())
async def bms_handler(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/bms Kuberaa 2025`")

    query = " ".join(message.command[1:])
    msg = await message.reply("🔍")

    img_url = get_google_poster(query + " bookmyshow+landscape+poster")
    image_url = await upload_to_imgbb(img_url)
    
    if img_url:
        await msg.edit_text(
        text=f"**BookMyShow Poster: {image_url}**\n\n**🌄 Landscape Poster:** [Click Here]({image_url})\n\n**🎬 {query} **\n\n**<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
        disable_web_page_preview=False,
        reply_markup=update_button
        )
        await client.send_message(chat_id=dump_chat, 
        text=f"**BookMyShow Poster: {img_url}**\n\n**🎬 {query} **\n\n<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
        disable_web_page_preview=False, reply_markup=update_button
        )
    else:
        await message.reply("❌ No image found.")

@Client.on_message(filters.command("crunchyroll") & filters.private)
async def pvt_crun_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("crunchyroll") & filters.group & force_sub_filter())
async def crunchyroll_handler(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/crunchyroll kaiju no. 8`")

    query = " ".join(message.command[1:])
    msg = await message.reply("🔍")

    img_url = get_google_poster(query + " crunchyrool+landscape+poster")
    image_url = await upload_to_imgbb(img_url)
    
    if img_url:
        await msg.edit_text(
        text=f"**Crunchyrool Poster: **{image_url}**\n\n**🌄 Landscape Poster:** [Click Here]({image_url})\n\n** 🎬 {query} **\n\n<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
        disable_web_page_preview=False,
        reply_markup=update_button
        )
        await client.send_message(chat_id=dump_chat, 
        text=f"**Crunchyrool Poster: {img_url}**\n\n**🌄 Landscape Poster:** [Click Here]({image_url})\n\n** 🎬 {query} **\n\n<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
        disable_web_page_preview=False, reply_markup=update_button
        )
    else:
        await message.reply("❌ No image found.")


#-----------------------OG OR TWITTER EXTRACT FROM META FUNCTION FOR DETAILS SEE AHA OR SHEMAROOME - - - - - - - - - - - - - - - 
# ✅ Universal Poster Extractor Function
def extract_ott_poster(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Try Twitter image
        twitter_meta = soup.find("meta", {"name": "twitter:image"})
        if twitter_meta and twitter_meta.get("content"):
            return twitter_meta.get("content")

        # Fallback to OG image
        og_meta = soup.find("meta", {"property": "og:image"})
        if og_meta and og_meta.get("content"):
            return og_meta.get("content")

    except Exception as e:
        print(f"[ERROR] Poster extract failed: {e}")

    return None



#-----------------------AHA POSTER EXTRACT FUNCTION - - - - - - - - - - - - - - - 
@Client.on_message(filters.command("aha") & filters.private)
async def pvt_aha_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("aha") & filters.group & force_sub_filter())
async def aha_handler(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    
    # Extract URL from command arguments or replied message
    url = None
    
    if len(message.command) > 1:
        url = message.command[1]
    elif message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text.strip()
    
    if not url:
        await message.reply("**ℹ️ Please provide a aha  URL after the command.**")
        return
    # extract URL logic ...
    await handle_generic_ott(client, message, url, "aha")



#-----------------------SHEMAROOME POSTER EXTRACT FUNCTION - - - - - - - - - - - - - - - 
@Client.on_message(filters.command("shemaroo") & filters.private)
async def pvt_shemaroo_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("shemaroo") & filters.group & force_sub_filter())
async def shemaroo_handler(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    
    # Extract URL from command arguments or replied message
    url = None
    
    if len(message.command) > 1:
        url = message.command[1]
    elif message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text.strip()
    
    if not url:
        await message.reply("**ℹ️ Please provide a shemaroo URL after the command.**")
        return
    # extract URL logic ...
    await handle_generic_ott(client, message, url, "shemaroo")


async def handle_generic_ott(client, message, url, ott_name):
    msg = await message.reply("🔍")
    
    poster_url = extract_ott_poster(url)

    if not poster_url:
        await msg.edit_text(f"⚠️ Could not fetch poster from {ott_name.title()}.")
        return

    image_url = await upload_to_imgbb(poster_url)
    title = url.split("/")[-1].replace('-', ' ').title()

    await msg.edit_text(
        text=f"**{ott_name.upper()} Poster: {image_url}**\n\n**🌄 Landscape Poster:** [Click Here]({image_url})\n\n** 🎬 {title} **\n\n**<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
        disable_web_page_preview=False,
        reply_markup=update_button
    )
    await client.send_message(chat_id =dump_chat, 
        text=f"**{ott_name.upper()} Poster: {poster_url}**\n\n**🌄 Landscape Poster:** [Click Here]({image_url})\n\n** 🎬 {title} **\n\n**<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
        disable_web_page_preview=False, reply_markup=update_button
    )



#-----------------------APPLE POSTER EXTRACT FUNCTION - - - - - - - - - - - - - - - 
def extract_apple_poster(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    image_url = None

    # Method 1: Twitter Image
    twitter_meta = soup.find("meta", {"name": "twitter:image"})
    if twitter_meta:
        image_url = twitter_meta.get("content")

    # Method 2: OG Image fallback
    if not image_url:
        og_meta = soup.find("meta", {"property": "og:image"})
        if og_meta:
            image_url = og_meta.get("content")

    return image_url


@Client.on_message(filters.command("apple") & filters.private)
async def pvt_apple_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("apple") & filters.group & force_sub_filter())
async def apple_command(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    
    # Extract URL from command arguments or replied message
    url = None
    
    if len(message.command) > 1:
        url = message.command[1]
    elif message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text.strip()
    
    if not url:
        await message.reply("**ℹ️ Please provide a apple tv URL after the command.**")
        return
    
    await handle_apple_request(client, message, url)


async def handle_apple_request(client, message, url):
    """Process apple URL and send poster"""
    # Validate URL format
    if not re.match(r'https?://(tv\.)?apple\.com/[\w\-]+', url):
        await message.reply("❌ Invalid apple tv Please provide a valid URL.\n\nExample: /apple `https://tv.apple.com/us/movie/love-kills/umc.cmc.6h7aqbqodyqkeyzvzkkdzjv13`")
        return
    
    try:
        # Send processing status
        msg = await message.reply("🔍")
        
        # Get poster URL
        poster_url = extract_apple_poster(url)
        image_url = await upload_to_imgbb(poster_url)

        if not poster_url:
            await msg.edit_text("⚠️ Failed to extract poster. The page structure might have changed or content is region-locked.")
            return

        match =  re.search(r'tv\.apple\.com\/[^\/]+\/(?:movie|show)\/([^\/]+)', url)
        if match:
            title = match.group(1).replace('-', ' ').title()
        else: 
            title = "Unknown Title" 
        
        await msg.edit_text(
            text=f"**AppleTv Poster: {image_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({image_url})\n\n** 🎬 {title} **\n\n**<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
        )
        await client.send_message(chat_id=dump_chat, 
            text=f"**AppleTv Poster: {poster_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({poster_url})\n\n**🎬 {title} **\n\n<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
        )
    except Exception as e:
        await message.reply(f"⚠️ Error: {e}")
        



#-----------------------YT THUMBNAIL EXTRACT FUNCTION - - - - - - - - - - - - - - - 
# Regex to extract video ID from any YouTube URL
YOUTUBE_REGEX = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
# Ordered list of thumbnail types
THUMBNAIL_QUALITIES = [
    "maxresdefault.jpg",
    "sddefault.jpg",
    "hqdefault.jpg",
    "mqdefault.jpg",
    "default.jpg"
]

async def get_available_thumbnail(video_id: str) -> str:
    base = f"https://img.youtube.com/vi/{video_id}/"
    async with aiohttp.ClientSession() as session:
        for quality in THUMBNAIL_QUALITIES:
            url = base + quality
            async with session.get(url) as resp:
                if resp.status == 200:
                    return url
    return None

@Client.on_message(filters.command(["yt", "youtube"]) & filters.private)
async def pvt_yr_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command(["yt", "youtube"]) & filters.group & force_sub_filter())
async def yt_thumbnail(client: Client, message: Message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    
    # Extract URL from command arguments or replied message
    if len(message.command) < 2:
        return await message.reply_text("🔗 Send a valid YouTube URL!\n\nUsage: `/yt <youtube_url>`")

    url = message.text.split(maxsplit=1)[1]
    match = re.search(YOUTUBE_REGEX, url)

    if not match:
        return await message.reply_text("**❌ Invalid YouTube URL format.**")

    video_id = match.group(1)
    thumbnail_url = await get_available_thumbnail(video_id)
    image_url = await upload_to_imgbb(thumbnail_url)

    if not thumbnail_url:
        return await message.reply_text("🚫 No thumbnail found for this video.", quote=True)
    msg = await message.reply("🔍")
    await asyncio.sleep(3)
    await msg.edit_text(
            text=f"**YtThumbnail: {image_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({image_url})\n<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
    )
    await client.send_message(chat_id =dump_chat, 
            text=f"**YtThumbnail: {image_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({image_url})\n<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
    )



#-----------------------AIRTEL POSTER EXTRACT FUNCTION - - - - - - - - - - - - - - - 
# Configure headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "DNT": "1"
}

def extract_airtel_poster(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the preload image link
        link_tag = soup.find("link", attrs={"rel": "preload", "as": "image"})
        if not link_tag:
            return None

        image_url = link_tag.get("href")
        if not image_url:
            return None

        # Extract the title
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"

        year = "Unknown"
        year_tag = soup.find("p", id="banner-content-release-year")
        if year_tag:
                match = re.search(r"\b(19|20)\d{2}\b", year_tag.text)
                if match:
                        year = match.group()

        ott_name = "Unknown" 
        match = re.search(r'/([A-Z]+)_(?:TVSHOW|MOVIE|LIVE)_', url)
        if match:
            ott_code = match.group(1).upper()
            ott_map = {
    "ZEEFIVE": "Zee5",
    "ZEE5": "Zee5",  # Some use this variant

    "SONYLIV": "SonyLiv",
    "HOTSTAR": "Hotstar",  # Disney+ Hotstar
    "AHA": "Aha",
    "HOICHOI": "Hoichoi",
    "EROSNOW": "Eros Now",
    "HUNGAMA": "Hungama Play",
    "LIONSGATE": "Lionsgate Play",
    "DISCOVERYPLUS": "Discovery+",
    "MANORAMAMAX": "Manorama Max",
    "VIU": "Viu",
    "VROTT": "VROTT",
    "SHEMAROOME": "ShemarooMe",
    "DAN": "DAN Play",
    "HAYU": "Hayu",
    "STINGRAY": "Stingray",
    "DIVO": "Divo",
    "DOCUBAY": "DocuBay",
    "FUSEPLUS": "Fuse+",
    "SHORTSTV": "ShortsTV",
    "EPICON": "Epic ON",
    "NUEFLIKS": "Nuefliks",
    "BINGE": "Tata Play Binge",
    "MXPLAYER": "MX Player",
    "JIOCINEMA": "JioCinema",
    "AMAZON": "Amazon Prime Video",
    "PRIME": "Amazon Prime Video",
    "APPLETV": "Apple TV+",
    "NETFLIX": "Netflix",  # not directly integrated, for reference

    # Regional / Special platforms
    "KOOKU": "Kooku",
    "ULLU": "Ullu",
    "CINEPRIME": "Cineprime",
    "HBO": "HBO Max",
    "NAAPTOL": "Naaptol",
    "WOWKIDZ": "WowKidz",
    "MUBI": "Mubi",
    "PLANETMARATHI": "Planet Marathi",
    "SUNNXT": "Sun NXT"
            }
    
            ott_name = ott_map.get(ott_code, ott_code.title())
            
        return image_url, title, year, ott_name
        

    except Exception as e:
        print("Error:", e)
        return None


@Client.on_message(filters.command("airtel") & filters.private)
async def pvt_airtel_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("airtel") & filters.group & force_sub_filter())
async def airtel_command(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    
    # Extract URL from command arguments or replied message
    url = None
    
    if len(message.command) > 1:
        url = message.command[1]
    elif message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text.strip()
    
    if not url:
        await message.reply("**ℹ️ Please provide a airtelXstream URL after the command.**")
        return
    
    await handle_airtel_request(client, message, url)


async def handle_airtel_request(client, message, url):
    """Process airtel URL and send poster"""
    # Validate URL format
    if not re.match(r'https?://(www\.)?airtelxstream\.in/[\w\-]+', url):
        await message.reply("❌ Invalid airtelxstream URL. Please provide a valid URL.\n\nExample: /airtel `https://www.airtelxstream.in/movies/detective-sherdil/ZEEFIVE_MOVIE_0-0-1z5742637`")
        return
    
    try:
        # Send processing status
        msg = await message.reply("🔍")
        
        # Get poster URL
        poster_url, title, year, ott_name = extract_airtel_poster(url)
        image_url = await upload_to_imgbb(poster_url)

        if not poster_url:
            await msg.edit_text("⚠️ Failed to extract poster. The page structure might have changed or content is region-locked.")
            return

        
        await msg.edit_text(
            text=f"**{ott_name} Poster: {image_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({image_url})\n\n** 🎬  {title} ({year})**\n\n<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
        )
        await client.send_message(chat_id =dump_chat, 
            text=f"**{ott_name} Poster: 🎬 {poster_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({image_url})\n\n** 🎬  {title} ({year})**\n\n<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
        )
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")




#-----------------------ZEE POSTER EXTRACT FUNCTION - - - - - - - - - - - - - - - 
# Configure headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
    "DNT": "1"
}


def clean_zee_url(url):
    """Remove transformation parameters from SonyLIV image URLs"""
    # Pattern to match the transformation segment
    pattern = r'(https://akamaividz2\.zee5\.com/image/upload/)[^/]+/(.*)'
    
    if match := re.match(pattern, url):
        base = match.group(1)
        path = match.group(2)
        return base + path
    return url

def extract_zee_poster(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        image_url = None
        title = "Untitled"

        # Method 1: Extract from JSON-LD videoObject script
        script_tag = soup.find('script', {'type': 'application/ld+json', 'id': 'videoObject'})
        if script_tag:
            try:
                import json
                json_data = json.loads(script_tag.string)

                # Title from JSON
                title = json_data.get('name', 'Untitled')

                # Handle thumbnailUrl
                thumbnail_url = json_data.get('thumbnailUrl')
                if thumbnail_url:
                    if isinstance(thumbnail_url, list) and len(thumbnail_url) > 0:
                        image_url = thumbnail_url[0]
                    elif isinstance(thumbnail_url, str):
                        image_url = thumbnail_url

                    # Clean Zee CDN URLs
                    if "akamaividz2.zee5.com" in image_url:
                        image_url = clean_zee_url(image_url)
            except Exception as json_error:
                print(f"JSON parse error: {json_error}")

        # Method 2: Fallback Twitter card
        if not image_url:
            twitter_meta = soup.find('meta', {'name': 'twitter:image'})
            if twitter_meta:
                image_url = twitter_meta.get('content')

        # Method 3: Fallback OG image
        if not image_url:
            og_meta = soup.find('meta', {'property': 'og:image'})
            if og_meta:
                image_url = og_meta.get('content')

        
        return image_url

    except Exception as e:
        print(f"Error extracting poster: {e}")
        return None, "Untitled"


@Client.on_message(filters.command("zee") & filters.private)
async def pvt_zee_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("zee") & filters.group & force_sub_filter())
async def zee_command(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    
    # Extract URL from command arguments or replied message
    url = None
    
    if len(message.command) > 1:
        url = message.command[1]
    elif message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text.strip()
    
    if not url:
        await message.reply("**ℹ️ Please provide a zee5 URL after the command.**")
        return
    
    await handle_zee_request(client, message, url)


async def handle_zee_request(client, message, url):
    """Process zee URL and send poster"""
    # Validate URL format
    if not re.match(r'https?://(www\.)?zee5\.com/[\w\-]+', url):
        await message.reply("❌ Invalid zee5 URL. Please provide a valid URL.\n\nExample: /zee `https://www.zee5.com/web-series/details/chhal-kapat-the-deception/0-6-4z5758569`")
        return
    
    try:
        # Send processing status
        msg = await message.reply("🔍")
        
        # Get poster URL
        poster_url = extract_zee_poster(url)
        
        if not poster_url:
            await msg.edit_text("⚠️ Failed to extract poster. The page structure might have changed or content is region-locked.")
            return

        # Split and find the part after 'details'
        parts = url.split("/")
        if "details" in parts:
            title_slug = parts[parts.index("details") + 1]
            title = title_slug.replace('-', ' ').title() 
        else:
            title = "Unknown Title" 
        

       
        await msg.edit_text(
            text=f"**Zee Poster: {poster_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({poster_url})\n\n** 🎬 {title} **\n\n<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
        )
        await client.send_message(chat_id =dump_chat, 
            text=f"**Zee Poster: {poster_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({poster_url})\n\n** 🎬 {title} **\n\n<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
        )
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")





#-----------------------AMAZON PRIME FUNCTION - - - - - - - - - - - - - - - 
# Initialize a persistent HTTP session
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

def extract_single(link):
    """Extract metadata for movies or single seasons"""
    res = session.get(link).text
    soup = BeautifulSoup(res, 'html.parser')
    script = soup.find('script', {'type': 'text/template'}, text=lambda t: t and 'props' in t)
    
    if not script:
        raise ValueError("Metadata script not found")
    
    data = json.loads(script.text)
    detail = data['props']['body'][0]['props']['atf']['state']['detail']['headerDetail']
    key = list(detail.keys())[0]
    media = detail[key]
    
    return {
        'landscape': media['images'].get('covershot'),
        'portrait': media['images'].get('packshot'),
        'title': media['title'],
        'year': media['releaseYear']
    }

def extract_amazon(link):
    """Determine if link is a movie or series and extract metadata"""
    res = session.get(link).text
    soup = BeautifulSoup(res, 'html.parser')
    
    # Check for season selector (indicates series)
    season_selector = soup.find('label', {'for': 'av-droplist-av-atf-season-selector'})
    
    if not season_selector:
        # Movie case
        movie_data = extract_single(link)
        return {'type': 'movie', **movie_data}
    
    # Series case - extract seasons
    season_list = season_selector.find_next('ul')
    seasons = {}
    
    for li in season_list.find_all('li'):
        season_name = li.find_all('span')[-1].text.strip()
        season_url = 'https://primevideo.com' + li.find('a')['href']
        seasons[season_name] = extract_single(season_url)
    
    # Get first season's metadata for overall info
    first_season = list(seasons.values())[0]
    return {
        'type': 'series',
        'title': first_season['title'],
        'year': first_season['year'],
        'seasons': seasons
    }



def format_movie_response(data):
    """Format movie response with posters as links"""
    response = f"**PrimeVideo Poster: {data['landscape']}\n\n🎬 **{data['title']} ({data['year']})**\n\n"
    
    # Landscape posters section
    response += "**🌄 Landscape Posters:**\n"
    if data.get('landscape'):
        response += f"1. [Click Here]({data['landscape']})\n"
    else:
        response += "`Not available`\n"
    
    # Portrait posters section
    response += "\n**🖼️ Portrait Posters:**\n"
    if data.get('portrait'):
        response += f"1. [Click Here]({data['portrait']})"
        response += "<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>"
    else:
        response += "`Not available`"
        response += "<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>"
    
    return response

def format_series_response(data):
    """Format series response with season selection buttons"""
    response = f"📺 **{data['title']}** ({data['year']})\n"
    response += f"**Type:** Series | **Seasons:** {len(data['seasons'])}\n\n"
    response += "**Select a season to get posters:**"
    
    # Create buttons for each season
    buttons = []
    for season_name in data['seasons'].keys():
        buttons.append(
            [InlineKeyboardButton(season_name, callback_data=f"season:{season_name}")]
        )
    
    return response, InlineKeyboardMarkup(buttons)

# Store user data temporarily
user_data = {}
@Client.on_message(filters.command("prime") & filters.private)
async def pvt_prime_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("prime") & filters.group & force_sub_filter())
async def prime_command(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    """Handle /prime command with Amazon Prime link"""
    # Extract link from command
    if len(message.command) < 2:
        await message.reply_text("** Please provide an Amazon Prime Video link after the command**.\nExample: `/prime https://www.primevideo.com/detail/...`")
        return
    
    link = message.text.split(" ", 1)[1].strip()
    
    # Validate Prime Video link
    if not re.match(r'https?://(?:www\.)?primevideo\.com', link, re.IGNORECASE):
        await message.reply_text("❌ Invalid Amazon Prime Video link. Please provide a valid link starting with `https://www.primevideo.com`")
        return
    
    status_msg = await message.reply("🔍 ")
    
    try:
        # Process link metadata
        result = extract_amazon(link)
        
        if result['type'] == 'movie':
            # Format and send movie response
            response = format_movie_response(result)
            await status_msg.edit_text(response, disable_web_page_preview=False, reply_markup=update_button)
            
        
        elif result['type'] == 'series':
            # Format series response with buttons
            response, keyboard = format_series_response(result)
            await status_msg.edit_text(response, disable_web_page_preview=False, reply_markup=keyboard)
            
            # Store season data for callback handling
            user_data[message.from_user.id] = {
                'seasons': result['seasons'],
                'title': result['title']
            }
    
    except Exception as e:
        await status_msg.edit_text(f"❌ Error processing link:\n`{str(e)}`\n\nAmazon might have changed their page structure.", parse_mode=enums.ParseMode.MARKDOWN)
        if message.from_user.id in user_data:
            del user_data[message.from_user.id]

@Client.on_callback_query(filters.regex(r'^season:'))
async def handle_season_selection(client, callback_query):
    """Handle season selection from inline buttons"""
    if not callback_query.data.startswith("season:"):
        # Ignore other callback types
        await callback_query.answer()
        return

    user_id = callback_query.from_user.id
    if user_id not in user_data:
        await callback_query.answer("Session expired. Please start over with /prime", show_alert=True)
        return
    
    # Extract season name from callback data
    season_name = callback_query.data.split(":", 1)[1]
    seasons = user_data[user_id]['seasons']
    
    if season_name not in seasons:
        await callback_query.answer("Season not found. Please try again", show_alert=True)
        return
    
    # Get season data
    season_info = seasons[season_name]
    
    # Format season response
    response = f"📺 **{user_data[user_id]['title']}**\n"
    response += f"**Season:** {season_name}\n\n"
    response += f"**🌄 Landscape Poster:**\n"
    response += f"› [Click Here]({season_info['landscape']})\n\n" if season_info.get('landscape') else "› Not available\n\n"
    response += f"**🖼️ Portrait Poster:**\n"
    response += f"› [Click Here]({season_info['portrait']})" if season_info.get('portrait') else "› Not available"
    response += "<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>"
    
    # Send response as new message
    await callback_query.message.reply_text(
        response,
        disable_web_page_preview=False,
        reply_to_message_id=callback_query.message.id, 
        reply_markup=update_button
    )
    await callback_query.answer()




@Client.on_message(filters.private & filters.user(HgBotz.ADMIN)  & filters.command(["stats"]))
async def all_db_users_here(client, message):
    start_t = time.time()
    rkn = await message.reply_text("Processing...")
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - client.uptime))    
    total_users = await total_user()
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rkn.edit(text=f"**--Bot Processed--** \n\n**Bot Started UpTime:** {uptime} \n**Bot Current Ping:** `{time_taken_s:.3f} ᴍꜱ` \n**All Bot Users:** `{total_users}`")


@Client.on_message(filters.private & filters.user(HgBotz.ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    if (message.reply_to_message):
        rkn = await message.reply_text("Bot Processing.\nI am checking all bot users.")
        all_users = await getid()
        tot = await total_user()
        success = 0
        failed = 0
        deactivated = 0
        blocked = 0
        await rkn.edit(f"bot ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ started...")
        async for user in all_users:
            try:
                time.sleep(1)
                await message.reply_to_message.copy(user['_id'])
                success += 1
            except errors.InputUserDeactivated:
                deactivated +=1
                await delete({"_id": user['_id']})
            except errors.UserIsBlocked:
                blocked +=1
                await delete({"_id": user['_id']})
            except Exception as e:
                failed += 1
                await delete({"_id": user['_id']})
                pass
            try:
                await rkn.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")
            except FloodWait as e:
                await asyncio.sleep(t.x)
        await rkn.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")
        
# Restart to cancell all process 
@Client.on_message(filters.private & filters.user(HgBotz.ADMIN) & filters.command("restart"))
async def restart_bot(b, m):
    rkn_msg = await b.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=m.chat.id)       
    await asyncio.sleep(3)
    await rkn_msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)
    



NOTIFICATION_CHANNEL_ID = -1002346166150
@Client.on_message(filters.command("start") & filters.all)
async def start_cmd(bot, message):
    user_id = int(message.from_user.id)
    reply_markup=InlineKeyboardMarkup(buttons)
    await insert(user_id)
    notification_text = f"🎉 New user started the bot: {message.from_user.mention} (ID: {user_id})"
    await bot.send_message(NOTIFICATION_CHANNEL_ID, notification_text)
    await message.reply_text(
        text=script.START_TXT.format(message.from_user.mention),
        disable_web_page_preview = False, 
        invert_media = True, 
        reply_markup=reply_markup)


@Client.on_message(filters.command("help") & filters.all)
async def help_cmd(client, message: Message):
        await message.reply_text(text=script.HELP_TXT, disable_web_page_preview = False, reply_markup=InlineKeyboardMarkup(help_buttons), invert_media=True) 
    

#-----------------------callback FUNCTION - - - - - - - - - - - - - - - 

@Client.on_callback_query(filters.regex('help'))
async def poster_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()  # Acknowledge the callback
    await callback_query.message.edit_text(text=script.HELP_TXT, reply_markup=InlineKeyboardMarkup(help_buttons), disable_web_page_preview=False, invert_media=True)


@Client.on_callback_query(filters.regex('games'))
async def games_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()  # Acknowledge the callback
    await callback_query.message.edit_text(text=script.GAMES_TXT, reply_markup=InlineKeyboardMarkup(games_buttons))

@Client.on_callback_query(filters.regex('back'))
async def back_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()  # Acknowledge the callback
    await callback_query.message.edit_text(text=script.HOME_TXT, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=False, invert_media=True)

@Client.on_callback_query(filters.regex('about'))
async def about_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()# Acknowledge the callback
    await callback_query.message.edit_text(text=script.ABOUT_TXT, reply_markup=InlineKeyboardMarkup(about_buttons), disable_web_page_preview=False, invert_media=True)




        
#-----------------------TMDB FUNCTION - - - - - - - - - - - - - - - 

#--------- poster.py-------
@Client.on_message(filters.command(["poster", "p", "pos"]) & filters.private)
async def pvt_cmd(client, message: Message):
        await message.reply_text(text="<b>This Cmnd Only Working In Below Group\n\nTo Find Any Movie Poster Join This Group And Use Cmnd</b>\n\nhttps://t.me/+Tm0jULCyPTJjYjM9", disable_web_page_preview = False) 
    
@Client.on_message(filters.command(["poster", "p", "pos"]) & filters.group & force_sub_filter())
async def poster_cmd(client, message: Message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @HGBOTZ_support")
    if len(message.command) < 2:
        return await message.reply(
            "Please provide a movie name.\n<code>/poster <title> <year(optional)></code>\n<b>Example:</b>\n<code>/poster Interstellar 2014</code>\n<code>/poster breaking bad</code>"
        )

    query = " ".join(message.command[1:])
    # Check for brackets
    if "(" in query or ")" in query:
        return await message.reply(
            "Please avoid using brackets in the query.\nExample: <code>/poster Animal 2023</code> instead of <code>/poster Animal (2023)</code>"
        )
    api_url = f"https://hgbots-hgbotz-s-projects.vercel.app/Test.php?query={query}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                return await message.reply("Failed to fetch data from API.")
            data = await resp.json()
   
    msg = await message.reply("🔍")
    await asyncio.sleep(3)
    
    reply_parts = [f"<blockquote><b>Movie:</b> {query}</blockquote>"]

    # English Backdrops
    en_backs = data.get("english_backdrops", [])
    if en_backs:
        en_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(en_backs)])
        reply_parts.append(f"<b>•English Landscape:</b>\n{en_text}")

    
    # Hindi Backdrops
    hi_backs = data.get("hindi_backdrops", [])
    if hi_backs:
        hi_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(hi_backs)])
        reply_parts.append(f"<b>• Hindi Landscape:</b>\n{hi_text}")


    if not en_backs and not hi_backs:
        all_backs = data.get("all_backdrops", [])
        if all_backs:
            all_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(all_backs)])
            reply_parts.append(f"<b>• Lang. Landscape:</b>\n<blockquote expandable>{all_text}</blockquote>")

    # Show default only if both English and Hindi backdrops are missing
    if not en_backs and not hi_backs:
        default_backs = data.get("default_backdrops", [])
        if default_backs:
            def_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(default_backs)])
            reply_parts.append(f"<b>• RAW Landscape:</b>\n{def_text}")

    all_logos = (
    data.get("logos", {}).get("en", []) +
    data.get("logos", {}).get("hi", []) +
    data.get("logos", {}).get("other", [])
    )

    if all_logos:
        logo_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(all_logos)])
        reply_parts.append(f"<b>•Logos Png:</b>\n<blockquote expandable>{logo_text}</blockquote>")
    
    # Posters
    posters = data.get("posters", [])
    if posters:
        poster_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(posters)])
        reply_parts.append(f"<b>•Portrait Posters:</b>\n{poster_text}")

    reply_parts.append("<b><blockquote>Powered By <a href='https://t.me/hgbotz'>𝙷𝙶𝙱𝙾𝚃ᶻ 🦋</a></blockquote></b>")
    update_button = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("💥 𝚄𝚙𝚍𝚊𝚝𝚎 𝙲𝚑𝚊𝚗𝚗𝚎𝚕", url="https://t.me/hgbotz")]
    ]
    )
    await msg.edit_text("\n\n".join(reply_parts), disable_web_page_preview=False, reply_markup=update_button)
#--------- update.py-------

# ====== Settings===================
CHANNEL_ID = -1002615965065 # <-- Apna Channel ID
CHANNEL_ID1 = -1002189546391
YOUR_USER_ID = [6359874284, 897584437]  # <-- Apna Telegram ID
# =======================

@Client.on_message(filters.command(["addmovie"]) & filters.user(YOUR_USER_ID))
async def addmovie_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply(
            "Please provide a movie name and optional year.\n\n<code>/addmovie Interstellar 2014</code>\n<code>/addmovie Breaking Bad</code>"
        )

    query = " ".join(message.command[1:])
    api_url = f"https://terabox-vercel-api-hgbotz-s-projects.vercel.app/query?query={query}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                return await message.reply("Failed to fetch movie details from API.")
            data = await resp.json()

    # Correct field names according to your JSON
    movie_name = data.get("matched_title", query)
    release_year = data.get("matched_year", "")
    media_type = data.get("media_type", "") 
    rating = data.get("rating", "") 
    overview = data.get("overview", "") 
    caption = f"#New_File_Added ✅ \n\n<b>📽️ 𝙵𝚒𝚕𝚎 𝙽𝚊𝚖𝚎 :- {movie_name} ({release_year})</b>\n\n<b>𝙼𝚎𝚍𝚒𝚊 𝚃𝚢𝚙𝚎 👉:-</b> {media_type} | <b>𝚁𝚊𝚝𝚒𝚗𝚐 💫:-</b> {rating} \n<b><blockquote>Powered by <a href='https://t.me/Movies_Eera'>Movies Eera 🦋</a></blockquote></b>"
    caption1 = f"#New_File_Added ✅ \n\n<b>📽️ 𝙵𝚒𝚕𝚎 𝙽𝚊𝚖𝚎 :- {movie_name} ({release_year})</b>\n\n<b>𝙼𝚎𝚍𝚒𝚊 𝚃𝚢𝚙𝚎 👉:-</b> {media_type} | <b>𝚁𝚊𝚝𝚒𝚗𝚐 💫:-</b> {rating} \n<b><blockquote>Powered by <a href='https://t.me/alsamovieszone'>ALSA MOVIES 🦋</a></blockquote></b>"
    image_url = None

    # Priority: English > Hindi > Default backdrops
    en_backs = data.get("english_backdrops", [])
    if en_backs:
        image_url = en_backs[0]
    else:
        hi_backs = data.get("hindi_backdrops", [])
        if hi_backs:
            image_url = hi_backs[0]
        else:
            def_backs = data.get("default_backdrops", [])
            if def_backs:
                image_url = def_backs[0]
            else:
                posters = data.get("posters", [])
                if posters:
                    image_url = posters[0]
    
    if not image_url:
        return await message.reply("No landscape image found for this movie.")

    # Invisible char trick for top preview
    text_to_send = f"<a href='{image_url}'>ㅤ</a> {caption}"
    text_to_send1 = f"<a href='{image_url}'>ㅤ</a> {caption1}"

    try:
        await client.send_message(
            chat_id=CHANNEL_ID,
            text=text_to_send,
            invert_media=True, 
            disable_web_page_preview=False  # Important for preview
        )
        await client.send_message(
            chat_id=CHANNEL_ID1,
            text=text_to_send1,
            invert_media=True, 
            reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Search Here 🔥Alsa🔥" , url="https://t.me/alsamovieszone")]]), 
            disable_web_page_preview=False  # Important for preview
        )
        await message.reply("✅ Movie posted successfully with preview on top!")
    except Exception as e:
        await message.reply(f"❌ Failed to post movie:\n<code>{e}</code>")

