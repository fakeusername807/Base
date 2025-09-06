import requests
from pyrogram import Client, filters, errors, types, enums 
from config import HgBotz
import os, asyncio, re, time, sys, random, html, httpx
from .database import total_user, getid, delete, insert, get_all_users, authorize_chat, unauthorize_chat, is_chat_authorized, get_all_authorized_chats
from pyrogram.errors import *
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto
from pyrogram.enums import ChatMemberStatus
from Script import script
import aiohttp
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
import json
from urllib.parse import unquote, parse_qs, urlparse
from PIL import Image
from io import BytesIO
from pymongo import MongoClient


 
#-----------------------INLINE BUTTONS - - - - - - - - - - - - - - - 
buttons = [[
                InlineKeyboardButton('📢 Uᴘᴅᴀᴛᴇ', url="https://t.me/MrSagarBots"),
                InlineKeyboardButton('♡ Cᴏɴᴛᴀᴄᴛ 🧛‍♂️ Aᴅᴍɪɴ ♡', url="https://t.me/MrSagar_RoBot")
            ],[
                InlineKeyboardButton('💁‍♀️ Hᴇʟᴘ', callback_data='help'),
                InlineKeyboardButton('😊 Aʙᴏᴜᴛ', callback_data='about')
            ]]

group_buttons = [[InlineKeyboardButton('Cʟɪᴄᴋ Tᴏ Sᴛᴀʀᴛ ᴍᴇ', url="https://t.me/MrSagarPoster_Bot?start=True")
               ],[
                  InlineKeyboardButton('📢 Uᴘᴅᴀᴛᴇ Cʜᴀɴɴᴇʟ', url="https://t.me/MrSagarBots")
                ]] 


back_button = [[
                 InlineKeyboardButton('♡ Cᴏɴᴛᴀᴄᴛ 🧛‍♂️ Aᴅᴍɪɴ ♡', url='https://t.me/MrSagar_RoBot'),
                 InlineKeyboardButton('📢 Uᴘᴅᴀᴛᴇ', url='https://t.me/MrSagarBots')
              ],[
                 InlineKeyboardButton('🔙 back', callback_data='back')
              ]]



help_buttons = [[        
        InlineKeyboardButton('♡ Cᴏɴᴛᴀᴄᴛ 🧛‍♂️ Aᴅᴍɪɴ ♡', url='https://t.me/MrSagar_RoBot'), 
        InlineKeyboardButton('BACK 🔙', callback_data='back')
        ]]

about_buttons = [[
        InlineKeyboardButton('📢 Uᴘᴅᴀᴛᴇ', url='https://t.me/MrSagarBots')
        ],[
        InlineKeyboardButton('💁‍♀️ Hᴇʟᴘ', callback_data='help'), 
        InlineKeyboardButton('🔙 back', callback_data='back')
        ]]

update_button = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("📢 Uᴘᴅᴀᴛᴇ Cʜᴀɴɴᴇʟ", url="https://t.me/MrSagarBots")]
    ]
)

dump_chat = -1002673922646
# 🧩 Environment Variables
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "MrSagarbots")  # e.g. @YourChannelUsername or -100xxxxxxxxxx
FSUB_TEXT = os.getenv("FSUB_TEXT", "<b>Nᴀᴍᴀsᴛʜᴇ {} Jɪ 😍 ,\n🌟Jᴏɪɴ Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ\n🌟Cᴀᴍᴇ Bᴀᴄᴋ Aɴᴅ Dᴏ Aɢᴀɪɴ👍🏻</b>")  # Image to show when not subscribed

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
        [InlineKeyboardButton("🔔 Jᴏɪɴ Uᴘᴅᴀᴛᴇ Cʜᴀɴɴᴇʟ", url=invite_link)]
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
            await message.reply("You are banned from using this bot 🚫")
        else:
            await message.reply(f"⚠️ Error: {data}")
        return False

    return filters.create(func)



@Client.on_message(filters.command(["auth", "authorize", "a"]) & filters.user(HgBotz.ADMIN))
async def auth_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Provide chat_id to authorize.\nUsage: `/auth -1001234567890`")
    try:
        chat_id = int(message.command[1])
        await authorize_chat(chat_id)
        await message.reply(f"Authorized Successfully ✅️")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@Client.on_message(filters.command(["unauth", "unauthorize", "ua"]) & filters.user(HgBotz.ADMIN))
async def unauth_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Provide chat_id to unauthorize.\nUsage: `/unauth -1001234567890`")
    try:
        chat_id = int(message.command[1])
        await unauthorize_chat(chat_id)
        await message.reply(f"Unauthorized Successfully 🚫")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

@Client.on_message(filters.command("auth_chat") & filters.user(HgBotz.ADMIN))
async def list_auth_chats(client, message):
    auth_chats = await get_all_authorized_chats()
    text = "**🔐 Authorized Chats:**\n"
    async for chat in auth_chats:
        text += f"`{chat['_id']}`\n"
    await message.reply(text if text.strip() != "**🔐 Authorized Chats:**" else "🚫 No authorized chats found.")

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
            form.add_field('name', 'MrSagarbots')  # Set custom word for URL
            
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
                        return f"https://i.ibb.co/{image_id}/MrSagarbots.jpg"
                    
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

@Client.on_message(filters.command("stkr") & filters.group & force_sub_filter())
async def sticker_cmd(client, message: Message):
    chat_id = message.chat.id

    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")

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
            return await message.reply("🔗 Please send an image URL or reply to an image.\nExample: `/stkr https://example.com/img.jpg`")

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

API_KEY = "df895dc044b279378af646e08aa596b68d82dcc8"
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
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("bms") & filters.group & force_sub_filter())
async def bms_handler(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
    
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/bms Kuberaa 2025`")

    query = " ".join(message.command[1:])
    msg = await message.reply("🔍")

    img_url = get_google_poster(query + " bookmyshow+landscape+poster")
    image_url = await upload_to_imgbb(img_url)
    
    if img_url:
        await msg.edit_text(
        text=f"**BookMyShow Poster: {image_url}**\n\n**🌄 Landscape Poster:** [Click Here]({image_url})\n\n**{query} **\n\n**<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
        disable_web_page_preview=False,
        reply_markup=update_button
        )
        await client.send_message(chat_id=dump_chat, 
        text=f"**BookMyShow Poster: {img_url}**\n\n**{query} **\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
        disable_web_page_preview=False, reply_markup=update_button
        )
    else:
        await message.reply("No image found ❌")

@Client.on_message(filters.command("croll") & filters.private)
async def pvt_crun_cmd(client, message: Message):
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("croll") & filters.group & force_sub_filter())
async def crunchyroll_handler(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
    
    if len(message.command) < 2:
        return await message.reply("❌ Usage: `/croll kaiju no. 8`")

    query = " ".join(message.command[1:])
    msg = await message.reply("🔍")

    img_url = get_google_poster(query + " crunchyrool+landscape+poster")
    image_url = await upload_to_imgbb(img_url)
    
    if img_url:
        await msg.edit_text(
        text=f"**Crunchyrool Poster: **{image_url}**\n\n**🌄 Landscape Poster:** [Click Here]({image_url})\n\n**{query} **\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
        disable_web_page_preview=False,
        reply_markup=update_button
        )
        await client.send_message(chat_id=dump_chat, 
        text=f"**Crunchyrool Poster: {img_url}**\n\n**🌄 Landscape Poster:** [Click Here]({image_url})\n\n**{query} **\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
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
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("aha") & filters.group & force_sub_filter())
async def aha_handler(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
    
    # Extract URL from command arguments or replied message
    url = None
    
    if len(message.command) > 1:
        url = message.command[1]
    elif message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text.strip()
    
    if not url:
        await message.reply("**ℹ️ Please provide a aha URL after the command.**")
        return
    # extract URL logic ...
    await handle_generic_ott(client, message, url, "aha")
 

#-----------------------SHEMAROOME POSTER EXTRACT FUNCTION - - - - - - - - - - - - - - - 
@Client.on_message(filters.command("shemaroome") & filters.private)
async def pvt_shemaroo_cmd(client, message: Message):
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("shemaroome") & filters.group & force_sub_filter())
async def shemaroo_handler(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
    
    # Extract URL from command arguments or replied message
    url = None
    
    if len(message.command) > 1:
        url = message.command[1]
    elif message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text.strip()
    
    if not url:
        await message.reply("**ℹ️ Please provide a aha URL after the command.**")
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
        text=f"**{ott_name.upper()} Poster: {image_url}**\n\n**🌄 Landscape Poster:** [Click Here]({image_url})\n\n**{title} **\n\n**<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
        disable_web_page_preview=False,
        reply_markup=update_button
    )
    await client.send_message(chat_id =dump_chat, 
        text=f"**{ott_name.upper()} Poster: {poster_url}**\n\n**🌄 Landscape Poster:** [Click Here]({image_url})\n\n**{title} **\n\n**<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
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
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("apple") & filters.group & force_sub_filter())
async def apple_command(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
    
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
            text=f"**AppleTv Poster: {image_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({image_url})\n\n**{title} **\n\n**<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
        )
        await client.send_message(chat_id=dump_chat, 
            text=f"**AppleTv Poster: {poster_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({poster_url})\n\n**{title} **\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
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
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 
    
@Client.on_message(filters.command(["yt", "youtube"]) & filters.group & force_sub_filter())
async def yt_thumbnail(client: Client, message: Message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
    
    # Extract URL from command arguments or replied message
    if len(message.command) < 2:
        return await message.reply("🔗 Send a valid YouTube URL!\n\nUsage: `/yt <youtube_url>`")

    url = message.text.split(maxsplit=1)[1]
    match = re.search(YOUTUBE_REGEX, url)

    if not match:
        return await message.reply("**❌ Invalid YouTube URL format.**")

    video_id = match.group(1)
    thumbnail_url = await get_available_thumbnail(video_id)
    image_url = await upload_to_imgbb(thumbnail_url)

    if not thumbnail_url:
        return await message.reply("No thumbnail found for this video 🚫", quote=True)
    msg = await message.reply("🔍")
    await asyncio.sleep(3)
    await msg.edit_text(
            text=f"**YtThumbnail: {image_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({image_url})\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
    )
    await client.send_message(chat_id =dump_chat, 
            text=f"**YtThumbnail: {image_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({image_url})\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
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
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("airtel") & filters.group & force_sub_filter())
async def airtel_command(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
    
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
            text=f"**{ott_name} Poster: {image_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({image_url})\n\n**{title} ({year})**\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
        )
        await client.send_message(chat_id =dump_chat, 
            text=f"**{ott_name} Poster: {poster_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({image_url})\n\n**{title} ({year})**\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
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
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 
    
@Client.on_message(filters.command("zee") & filters.group & force_sub_filter())
async def zee_command(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
    
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
        image_url = await upload_to_imgbb(poster_url)
     
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
            text=f"**Zee Poster: {image_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({poster_url})\n\n**{title} **\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
        )
        await client.send_message(chat_id =dump_chat, 
            text=f"**Zee Poster: {poster_url}**\n\n**🌄 Landscape Posters:**\n1. [Click Here]({poster_url})\n\n**{title} **\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>",
            disable_web_page_preview=False, reply_markup=update_button
        )
        
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

# -----------------------NETFLIX POSTER FUNCTION -----------------------

@Client.on_message(filters.command("nf") & filters.private)
async def pvt_nf_cmd(client, message: Message):
    await message.reply_text(
        text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>",
        disable_web_page_preview=False
    )

@Client.on_message(filters.command("nf") & filters.group & force_sub_filter())
async def netflix_handler(client, message: Message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")

    if not message.from_user:
        return await message.reply("⚠️ Cannot detect sender (maybe sent from a channel).", quote=True)

    if len(message.command) < 2:
        return await message.reply("** Please provide an Netflix link after the command**.\nExample: `/nf https://www.netflix.com/in/title/........`", quote=True)

    url = message.command[1].strip()
    match = re.search(r'/title/(\d+)', url)
    if not match:
        return await message.reply("❌ Invalid Netflix URL!", quote=True)

    movie_id = match.group(1)
    api_url = f"https://netflix-en.gregory24thom-ps-on23-96.workers.dev/?movieid={movie_id}"

    msg = await message.reply("🔍")

    try:
        async with httpx.AsyncClient(timeout=10) as client_http:
            resp = await client_http.get(api_url)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        return await msg.edit_text(f"❌ Failed to fetch data: {e}")

    if data.get("status") != "success":
        return await msg.edit_text("❌ Movie/Series not found!")

    video = data.get("metadata", {}).get("video", {})
    title = video.get("title", "N/A")
    type_ = video.get("type", "movie")
    poster_url = video.get("artwork", [{}])[0].get("url", "")

    if type_ == "show" and video.get("seasons"):
        first_season = video["seasons"][0]
        season_name = (
            first_season.get("longName")
            or first_season.get("shortName")
            or f"Season {first_season.get('seq', 1)}"
        )
        season_year = first_season.get("year") or ""
        caption = f"<b>{title} - {season_name} ({season_year})</b>\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>"
    else:
        year = video.get("year", "N/A")
        caption = f"<b>{title} ({year})</b>\n\n<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>"

    if poster_url:
        await msg.edit_text(
            f"**Netflix Poster: {poster_url}**\n\n{caption}",
            disable_web_page_preview=False,
            reply_markup=update_button
        )
        await client.send_message(
            chat_id=dump_chat,
            text=f"**Netflix Poster: {poster_url}**\n\n{caption}",
            disable_web_page_preview=False,
            reply_markup=update_button
        )
    else:
        await msg.edit_text(caption, disable_web_page_preview=False)


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
    response = f"<b>PrimeVideo Poster</b>: <b>{data['landscape']}</b>\n\n<b>{data['title']} ({data['year']})</b>\n\n"
    
    # Landscape posters section
    response += "<b>🌄 Landscape Posters:</b>\n"
    if data.get('landscape'):
        response += f"1. [Click Here]({data['landscape']})\n"
    else:
        response += "`Not available`\n"
    
    # Portrait posters section
    response += "\n<b>🖼️ Portrait Posters:</b>\n"
    if data.get('portrait'):
        response += f"1. [Click Here]({data['portrait']})\n\n"
        response += "<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>"
    else:
        response += "`Not available`"
        response += "<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>"
    
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
@Client.on_message(filters.command(["prime", "pv"]) & filters.private)
async def pvt_prime_cmd(client, message: Message):
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 
    
@Client.on_message(filters.command(["prime", "pv"]) & filters.group & force_sub_filter())
async def prime_command(client, message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
    """Handle /prime command with Amazon Prime link"""
    # Extract link from command
    if len(message.command) < 2:
        await message.reply_text("** Please provide an Amazon Prime Video link after the command**.\nExample: `/pv or /prime https://www.primevideo.com/detail/...`")
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
    response += f"› [Click Here]({season_info['portrait']})" if season_info.get('portrait') else "› Not available\n\n"
    response += "<b><blockquote>Powered By <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>"
    
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
    

NOTIFICATION_CHANNEL_ID = -1002470928284
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
@Client.on_message(filters.command(["poster", "pos"]) & filters.private)
async def pvt_cmd(client, message: Message):
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 
    
@Client.on_message(filters.command(["poster", "pos"]) & filters.group & force_sub_filter())
async def poster_cmd(client, message: Message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
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
    
    reply_parts = [f"<blockquote>{query}</blockquote>"]

    # English Backdrops
    en_backs = data.get("english_backdrops", [])
    if en_backs:
        en_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(en_backs)])
        reply_parts.append(f"<b>🇺🇸 English Landscape</b>\n<blockquote expandable>{en_text}</blockquote>")

    
    # Hindi Backdrops
    hi_backs = data.get("hindi_backdrops", [])
    if hi_backs:
        hi_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(hi_backs)])
        reply_parts.append(f"<b>🇮🇳 Hindi Landscape</b>\n<blockquote expandable>{hi_text}</blockquote>")


    if not en_backs and not hi_backs:
        all_backs = data.get("all_backdrops", [])
        if all_backs:
            all_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(all_backs)])
            reply_parts.append(f"<b>🌐 Lang. Landscape</b>\n<blockquote expandable>{all_text}</blockquote>")

    # Show default only if both English and Hindi backdrops are missing
    if not en_backs and not hi_backs:
        default_backs = data.get("default_backdrops", [])
        if default_backs:
            def_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(default_backs)])
            reply_parts.append(f"<b>🌐 RAW Landscape</b>\n<blockquote expandable>{def_text}</blockquote>")

    all_logos = (
    data.get("logos", {}).get("en", []) +
    data.get("logos", {}).get("hi", []) +
    data.get("logos", {}).get("other", [])
    )

    if all_logos:
        logo_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(all_logos)])
        reply_parts.append(f"<b>🎯 Logos (PNG)</b>\n<blockquote expandable>{logo_text}</blockquote>")
    
    # Posters
    posters = data.get("posters", [])
    if posters:
        poster_text = "\n".join([f"{i+1}. <a href='{url}'>Click Here</a>" for i, url in enumerate(posters)])
        reply_parts.append(f"<b>🖼️ Portrait Posters</b>\n<blockquote expandable>{poster_text}</blockquote>")

    reply_parts.append("<b>🚀 Powered By @MrSagarbots</b>")
    update_button = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("📢 Uᴘᴅᴀᴛᴇ Cʜᴀɴɴᴇʟ", url="https://t.me/MrSagarBots")]
    ]
    )
    await msg.edit_text("\n\n".join(reply_parts), disable_web_page_preview=False, reply_markup=update_button)

# ================== TMDB Config ==================

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "fe6745c215b5ed09da847340eae06b9e")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"


# In-memory session store
poster_cache = {}

LANGS = ["en", "hi", "bn"]  # supported languages


def filter_with_fallback(items, cond, langs=LANGS):
    """Filter by langs, fallback to null iso_639_1 if nothing found"""
    filtered = [i for i in items if cond(i) and i.get("iso_639_1") in langs]
    if not filtered:
        filtered = [i for i in items if cond(i) and not i.get("iso_639_1")]
    return filtered


# ---------------- Search ----------------
@Client.on_message(filters.command(["posters", "p"]) & filters.private)
async def pvt_cmd(client, message: Message):
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False)


@Client.on_message(filters.command(["posters", "p"]) & filters.group & force_sub_filter())
async def posters_cmd(client, message: Message):
    chat_id = message.chat.id
    if not await is_chat_authorized(chat_id):
        return await message.reply("❌ This chat is not authorized to use this command. Contact @MrSagar_RoBot")
     
    query = " ".join(message.command[1:])
    if not query:
        return await message.reply_text("⚡ Usage: `/p movie name`", quote=True)

    # Detect year like "(2024)" or "2024"
    year = None
    match = re.search(r"\(?(\d{4})\)?$", query.strip())
    if match:
        year = match.group(1)
        query = query[:match.start()].strip()

    url = f"{TMDB_BASE_URL}/search/multi"

    # First try with year filter
    params = {"api_key": TMDB_API_KEY, "query": query}
    if year:
        params["year"] = year  # movies
        params["first_air_date_year"] = year  # TV shows
    r = requests.get(url, params=params).json()
    results = r.get("results", [])

    # Fallback without year if nothing found
    if not results and year:
        params = {"api_key": TMDB_API_KEY, "query": query}
        r = requests.get(url, params=params).json()
        results = r.get("results", [])

    if not results:
        return await message.reply_text("❌ No results found.", quote=True)

    results = results[:10]  # max 10 results
    buttons = []
    for res in results:
        title = res.get("title") or res.get("name")
        year_res = (res.get("release_date") or res.get("first_air_date") or "????")[:4]
        media_type = res.get("media_type", "movie")
        tmdb_id = res.get("id")
        buttons.append([
            InlineKeyboardButton(f"{title} ({year_res})", callback_data=f"select_{media_type}_{tmdb_id}")
        ])

    buttons.append([InlineKeyboardButton("❌ Close", callback_data="close")])

    await message.reply_text(
        "**🔎 Search Results:**",
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )


# ---------------- Select result ----------------
@Client.on_callback_query(filters.regex(r"select_(movie|tv)_(\d+)"))
async def select_result(client, cq: CallbackQuery):
    media_type, tmdb_id = cq.data.split("_")[1:]
    tmdb_id = int(tmdb_id)

    url = f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}/images"
    params = {"api_key": TMDB_API_KEY, "include_image_language": "en,hi,bn,null"}
    images = requests.get(url, params=params).json()

    title = "Unknown"
    year = "N/A"
    try:
        details = requests.get(f"{TMDB_BASE_URL}/{media_type}/{tmdb_id}", params={"api_key": TMDB_API_KEY}).json()
        title = details.get("title") or details.get("name") or "Unknown"
        year = (details.get("release_date") or details.get("first_air_date") or "N/A")[:4]
    except:
        pass

    poster_cache[cq.from_user.id] = {
        "id": tmdb_id,
        "type": media_type,
        "title": title,
        "year": year,
        "images": images
    }

    portrait_items = filter_with_fallback(images.get("posters", []), lambda p: p.get("height", 0) > p.get("width", 0))
    landscape_items = filter_with_fallback(images.get("posters", []), lambda p: p.get("width", 0) > p.get("height", 0)) + \
                      filter_with_fallback(images.get("backdrops", []), lambda b: b.get("width", 0) >= b.get("height", 0))
    logo_items = filter_with_fallback(images.get("logos", []), lambda l: True)

    keyboard = [
        [InlineKeyboardButton(f"🖼 Portrait ({len(portrait_items)})", callback_data="show:portrait:0")],
        [InlineKeyboardButton(f"🌅 Landscape ({len(landscape_items)})", callback_data="show:landscape:0")],
        [InlineKeyboardButton(f"🔖 Logos ({len(logo_items)})", callback_data="show:logo:0")]      
    ]

    await cq.message.edit_text(
        f"<b>{title} ({year})</b>\nSelect Poster Type:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- Show category ----------------
@Client.on_callback_query(filters.regex(r"^show:(portrait|landscape|logo):\d+$"))
async def show_category(client, cq: CallbackQuery):
    _, category, idx = cq.data.split(":")
    idx = int(idx)

    data = poster_cache.get(cq.from_user.id)
    if not data:
        return await cq.answer("⚠️ Try /p again", show_alert=True)

    images = data["images"]

    if category == "portrait":
        items = filter_with_fallback(images.get("posters", []), lambda p: p.get("height", 0) > p.get("width", 0))
    elif category == "landscape":
        items = filter_with_fallback(images.get("posters", []), lambda p: p.get("width", 0) > p.get("height", 0)) + \
                filter_with_fallback(images.get("backdrops", []), lambda b: b.get("width", 0) >= b.get("height", 0))
    else:
        items = filter_with_fallback(images.get("logos", []), lambda l: True)

    if not items:
        return await cq.edit_message_text("❌ No images found.")

    idx = max(0, min(idx, len(items) - 1))
    img = items[idx]

    url = f"{TMDB_IMAGE_BASE}{img['file_path']}"
    lang = img.get("iso_639_1") or "N/A"
    w, h = img.get("width", "?"), img.get("height", "?")
    tmdb_link = f"https://www.themoviedb.org/{data['type']}/{data['id']}"

    caption = (
        f"<b>{data['title']} ({data['year']})</b>\n\n"
        f"<b>• Category: {category.capitalize()}</b>\n\n"
        f"<b>• Language: {lang}</b>\n\n"
        f"<b>• Size: {w}x{h}</b>\n\n"
        f"🔗 <a href='{tmdb_link}'>TMDB Link</a>\n\n"
        f"<b>🚀 Powered By @MrSagarbots</b>"
    )

    buttons = [
        [
            InlineKeyboardButton("⬅️ Prev", callback_data=f"nav:{category}:{idx-1}"),
            InlineKeyboardButton(f"{idx+1}/{len(items)}", callback_data="noop"),
            InlineKeyboardButton("Next ➡️", callback_data=f"nav:{category}:{idx+1}"),
        ],
    ]

    await cq.message.edit_media(
        media=InputMediaPhoto(media=url, caption=caption),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ---------------- Navigation ----------------
@Client.on_callback_query(filters.regex(r"^nav:(portrait|landscape|logo):(-?\d+)$"))
async def navigate(client, cq: CallbackQuery):
    _, category, pos = cq.data.split(":")
    idx = int(pos)

    data = poster_cache.get(cq.from_user.id)
    if not data:
        return await cq.answer("⚠️ Session expired. Use /p again", show_alert=True)

    images = data["images"]

    if category == "portrait":
        items = filter_with_fallback(images.get("posters", []), lambda p: p.get("height", 0) > p.get("width", 0))
    elif category == "landscape":
        items = filter_with_fallback(images.get("posters", []), lambda p: p.get("width", 0) > p.get("height", 0)) + \
                filter_with_fallback(images.get("backdrops", []), lambda b: b.get("width", 0) >= b.get("height", 0))
    else:
        items = filter_with_fallback(images.get("logos", []), lambda l: True)

    if not items:
        return await cq.edit_message_text("❌ No images found.")

    idx = max(0, min(idx, len(items) - 1))
    img = items[idx]

    url = f"{TMDB_IMAGE_BASE}{img['file_path']}"
    lang = img.get("iso_639_1") or "N/A"
    w, h = img.get("width", "?"), img.get("height", "?")
    tmdb_link = f"https://www.themoviedb.org/{data['type']}/{data['id']}"

    caption = (
        f"<b>{data['title']} ({data['year']})</b>\n\n"
        f"<b>• Category: {category.capitalize()}</b>\n\n"
        f"<b>• Language: {lang}</b>\n\n"
        f"<b>• Size: {w}x{h}</b>\n\n"
        f"🔗 <a href='{tmdb_link}'>TMDB Link</a>\n\n"
        f"<b>🚀 Powered By @MrSagarbots</b>"
    )

    buttons = [
        [
            InlineKeyboardButton("⬅️ Prev", callback_data=f"nav:{category}:{idx-1}"),
            InlineKeyboardButton(f"{idx+1}/{len(items)}", callback_data="noop"),
            InlineKeyboardButton("Next ➡️", callback_data=f"nav:{category}:{idx+1}"),
        ],
    ]

    await cq.message.edit_media(
        media=InputMediaPhoto(media=url, caption=caption),
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ---------------- Back to Types ----------------
@Client.on_callback_query(filters.regex("^back_to_types$"))
async def back_to_types(client, cq: CallbackQuery):
    data = poster_cache.get(cq.from_user.id)
    if not data:
        return await cq.answer("⚠️ Session expired. Use /posters again", show_alert=True)

    images = data["images"]
    portrait_items = filter_with_fallback(images.get("posters", []), lambda p: p.get("height", 0) > p.get("width", 0))
    landscape_items = filter_with_fallback(images.get("posters", []), lambda p: p.get("width", 0) > p.get("height", 0)) + \
                      filter_with_fallback(images.get("backdrops", []), lambda b: b.get("width", 0) >= b.get("height", 0))
    logo_items = filter_with_fallback(images.get("logos", []), lambda l: True)

    keyboard = [
        [InlineKeyboardButton(f"🖼 Portrait ({len(portrait_items)})", callback_data="show:portrait:0")],
        [InlineKeyboardButton(f"🌅 Landscape ({len(landscape_items)})", callback_data="show:landscape:0")],
        [InlineKeyboardButton(f"🔖 Logos ({len(logo_items)})", callback_data="show:logo:0")],
    ]

    await cq.message.edit_text(
        f"<b>{data['title']} ({data['year']})</b>\nSelect Poster Type:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- Close ----------------
@Client.on_callback_query(filters.regex("^close$"))
async def close_btn(client, cq: CallbackQuery):
    try:
        await cq.message.delete()
    except Exception:
        pass


@Client.on_callback_query(filters.regex("noop"))
async def noop_btn(client, cq: CallbackQuery):
    await cq.answer()

#--------- update.py-------

# ====== Settings===================
CHANNEL_ID = -1002470928284 # <-- Apna Channel ID
CHANNEL_ID1 = -1002470928284
YOUR_USER_ID = [7965786027, 5355635400]  # <-- Apna Telegram ID
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
    caption = f"#New_File_Added ✅ \n\n<b>📽️ 𝙵𝚒𝚕𝚎 𝙽𝚊𝚖𝚎 :- {movie_name} ({release_year})</b>\n\n<b>𝙼𝚎𝚍𝚒𝚊 𝚃𝚢𝚙𝚎 👉:-</b> {media_type} | <b>𝚁𝚊𝚝𝚒𝚗𝚐 💫:-</b> {rating} \n<b><blockquote>Powered by <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>"
    caption1 = f"#New_File_Added ✅ \n\n<b>📽️ 𝙵𝚒𝚕𝚎 𝙽𝚊𝚖𝚎 :- {movie_name} ({release_year})</b>\n\n<b>𝙼𝚎𝚍𝚒𝚊 𝚃𝚢𝚙𝚎 👉:-</b> {media_type} | <b>𝚁𝚊𝚝𝚒𝚗𝚐 💫:-</b> {rating} \n<b><blockquote>Powered by <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>"
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
                    [InlineKeyboardButton("Search Here" , url="https://t.me/MrSagarbots")]]), 
            disable_web_page_preview=False  # Important for preview
        )
        await message.reply("✅ Movie posted successfully with preview on top!")
    except Exception as e:
        await message.reply(f"❌ Failed to post movie:\n<code>{e}</code>")

#-----------------------TELEGRAM VIDEO FILE EXTRACT FUNCTION - - - - - - - - - - - - - - - 

@Client.on_message(filters.command("extract_thumb") & filters.private)
async def pvt_cmd(client, message: Message):
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False) 

@Client.on_message(filters.command("extract_thumb") & filters.group & force_sub_filter())
async def extract_telegram_thumb(client: Client, message: Message):
    reply = message.reply_to_message

    # Not a reply? Tell user to reply with media
    if not reply:
        return await message.reply("🖼 Reply with Telegram Video")

    # Not a video? Still guide user
    if not reply.video:
        return await message.reply("🖼 Reply with Telegram Video")

    # Video but no thumbnail
    if not reply.video.thumbs:
        return await message.reply("⚠️ No thumbnail found in this video.")

    # Download and send thumbnail
    thumb_path = await client.download_media(reply.video.thumbs[0])
    await message.reply_photo(photo=thumb_path, caption="✅ <b>Extracted Telegram Video Thumbnail</b>\n\n<b><blockquote>Powered by <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote></b>")

#----------------------- Web Series Episode Auto Renamer -----------------------

@Client.on_message(filters.command("rename") & filters.private)
async def pvt_cmd(client, message: Message):
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False)

@Client.on_message(filters.command("rename") & filters.group & force_sub_filter())
async def rename_episode(client: Client, message: Message):
    reply = message.reply_to_message

    TMDB_API_KEY = "fe6745c215b5ed09da847340eae06b9e"  # Replace with your real key

    if len(message.command) < 2:
        return await message.reply("Send like: `/rename The Boys S01E01`")

    query = message.text.split(None, 1)[1]

    match = re.search(r'(.*?)[\s\-]*(S(\d{1,2})E(\d{1,2}))', query, re.IGNORECASE)
    if not match:
        return await message.reply("❌ Could not parse season/episode. Try like:\n`/rename Stranger Things S02E03`")

    show_name = match.group(1).strip()
    season_num = int(match.group(3))
    episode_num = int(match.group(4))

    # Step 1: Search TMDB for show
    async with httpx.AsyncClient() as client_http:
        search_url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={show_name}"
        res = await client_http.get(search_url)
        data = res.json()

        if not data.get("results"):
            return await message.reply("❌ No TV show found on TMDB.")

        show = data["results"][0]
        show_id = show["id"]
        title = show["name"]

        # Step 2: Get episode info
        episode_url = f"https://api.themoviedb.org/3/tv/{show_id}/season/{season_num}/episode/{episode_num}?api_key={TMDB_API_KEY}"
        ep_res = await client_http.get(episode_url)
        ep_data = ep_res.json()

        ep_title = ep_data.get("name")
        ep_air_date = ep_data.get("air_date")

        if not ep_title:
            return await message.reply("❌ Could not find that episode.")

        await message.reply(
            f"🎬 **{title}** - Season {season_num} Episode {episode_num}\n"
            f"📝 **Title:** {ep_title}\n"
            f"📅 **Air Date:** {ep_air_date or 'N/A'}\n\n"
            f"**<blockquote>Powered by <a href='https://t.me/MrSagarbots'>MrSagarbots</a></blockquote>**"
        )
#--------- OTT Availability Checker -----------------

TMDB_API_KEY = "fe6745c215b5ed09da847340eae06b9e"

@Client.on_message(filters.command("where") & filters.private)
async def pvt_cmd(client, message: Message):
        await message.reply_text(text="<b>This command is only available in specific groups.\nContact Admin @MrSagar_RoBot to get the link.</b>", disable_web_page_preview = False)

@Client.on_message(filters.command("where") & filters.group & force_sub_filter())
async def where_stream(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❗ Usage: `/where <movie/show name>`")

    query = message.text.split(None, 1)[1]

    async with httpx.AsyncClient() as session:
        # Search on TMDB
        search_url = "https://api.themoviedb.org/3/search/multi"
        params = {
            "api_key": TMDB_API_KEY,
            "query": query
        }
        r = await session.get(search_url, params=params)
        results = r.json().get("results", [])

        if not results:
            return await message.reply("❌ No results found.")

        result = results[0]
        tmdb_id = result["id"]
        title = result.get("title") or result.get("name")
        year = (result.get("release_date") or result.get("first_air_date") or "")[:4]
        media_type = result["media_type"]

        # Fetch watch providers
        provider_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/watch/providers"
        r2 = await session.get(provider_url, params={"api_key": TMDB_API_KEY})
        providers = r2.json().get("results", {}).get("IN", {})  # Use 'IN' for India

        flatrate = providers.get("flatrate", [])
        rent = providers.get("rent", [])
        buy = providers.get("buy", [])

        if not (flatrate or rent or buy):
            return await message.reply(f"ℹ️ **{title} ({year})** not available on any OTT in India.")

        text = f"🎬 **{title} ({year})**\n\n"

        if flatrate:
            text += "<b>📺 Streaming on:</b>\n" + "\n".join(f"• {x['provider_name']}" for x in flatrate) + "\n\n"
        if rent:
            text += "<b>💸 Available to Rent:</b>\n" + "\n".join(f"• {x['provider_name']}" for x in rent) + "\n\n"
        if buy:
            text += "<b>🛒 Available to Buy:</b>\n" + "\n".join(f"• {x['provider_name']}" for x in buy)

        await message.reply(text.strip())

# ================== CAPTION CHANGER SECTION ==================
# MongoDB setup for storing caption templates
mongo_client = MongoClient(HgBotz.DB_URL)
db = mongo_client[HgBotz.DB_NAME]
templates_col = db["caption_templates"]

# TMDB API key directly from environment
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "fe6745c215b5ed09da847340eae06b9e")

# Helper: format file size
def format_size(size):
    if not size:
        return "Unknown"
    power = 1024
    n = 0
    units = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size >= power and n < 4:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}"

# Helper: get quality
def extract_quality_from_name(file_name, height=None):
    match = re.search(r'(\d{3,4}p)', file_name.lower())
    if match:
        return match.group(1)
    if height:
        if height >= 1080:
            return "1080p"
        elif height >= 720:
            return "720p"
        elif height >= 480:
            return "480p"
    return "Unknown"

# Fetch episode name from TMDB
def get_tmdb_episode_name(file_name, season, episode):
    if season == "Unknown" or episode == "Unknown" or not TMDB_API_KEY:
        return "Unknown"
    show_name = re.split(r'[Ss]\d{1,2}[Ee]\d{1,2}', file_name)[0].replace('.', ' ').strip()
    if not show_name:
        return "Unknown"
    try:
        search_url = "https://api.themoviedb.org/3/search/tv"
        params = {"api_key": TMDB_API_KEY, "query": show_name}
        resp = requests.get(search_url, params=params, timeout=10).json()
        if not resp.get("results"):
            return "Unknown"
        show_id = resp["results"][0]["id"]
        ep_url = f"https://api.themoviedb.org/3/tv/{show_id}/season/{season[1:]}/episode/{episode[1:]}"
        ep_resp = requests.get(ep_url, params={"api_key": TMDB_API_KEY}, timeout=10).json()
        return ep_resp.get("name", "Unknown")
    except:
        return "Unknown"

# Extract info from video
def extract_file_info(video_msg):
    video = video_msg.video
    file_name = video.file_name or ""
    caption = video_msg.caption or ""

    year_match = re.search(r'(19\d{2}|20\d{2})', file_name)
    year = year_match.group(1) if year_match else "Unknown"

    langs = []
    for lang in ["Hindi", "English", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali", "Bangla", "Punjabi", "Gujarati", "Marathi", "Spanish", "Korean", "Chinese", "Japanese", "German"]:
        if re.search(lang, file_name, re.IGNORECASE) or re.search(lang, caption, re.IGNORECASE):
            langs.append(lang)
    audio_langs = ", ".join(langs) if langs else "Unknown"

    subs_match = re.findall(r'([a-zA-Z]+)(?=\s*sub)', file_name + " " + caption, re.IGNORECASE)
    subtitles = ", ".join(set([s.title() for s in subs_match])) if subs_match else "None"

    season_match = re.search(r'[Ss](\d{1,2})', file_name)
    season = f"S{season_match.group(1).zfill(2)}" if season_match else "Unknown"

    episode_match = re.search(r'[Ee](\d{1,2})', file_name)
    episode = f"E{episode_match.group(1).zfill(2)}" if episode_match else "Unknown"

    episode_name = get_tmdb_episode_name(file_name, season, episode)

    return {
        "file_name": file_name or "Unknown",
        "file_caption": caption,
        "file_size": format_size(video.file_size),
        "audio": audio_langs,
        "quality": extract_quality_from_name(file_name, video.height),
        "Years": year,
        "duration": f"{video.duration // 60} min" if video.duration else "Unknown",
        "subtitles": subtitles,
        "season": season,
        "episode": episode,
        "episode_name": episode_name
    }

# Format caption with placeholders
def format_caption(template, file_info):
    return template.format(
        file_name=file_info.get("file_name", "Unknown"),
        file_caption=file_info.get("file_caption", ""),
        file_size=file_info.get("file_size", "Unknown"),
        audio=file_info.get("audio", "N/A"),
        quality=file_info.get("quality", "Unknown"),
        Years=file_info.get("Years", "Unknown"),
        duration=file_info.get("duration", "Unknown"),
        subtitles=file_info.get("subtitles", "Unknown"),
        season=file_info.get("season", "Unknown"),
        episode=file_info.get("episode", "Unknown"),
        episode_name=file_info.get("episode_name", "Unknown")
    )

pending_caption = {}
AUTO_DELETE_OLD = True

@Client.on_message(filters.command("change_caption"))
async def change_caption_cmd(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply_text("❌ Please reply to a video file.")

    file_info = extract_file_info(message.reply_to_message)
    user_id = message.from_user.id

    saved_template = templates_col.find_one({"user_id": user_id})
    if saved_template:
        new_caption = format_caption(saved_template["template"], file_info)
        await message.reply_to_message.reply_video(
            video=message.reply_to_message.video.file_id,
            caption=new_caption
        )
        if AUTO_DELETE_OLD:
            await message.reply_to_message.delete()
        return

    pending_caption[user_id] = {
        "file_info": file_info,
        "file_id": message.reply_to_message.video.file_id,
        "old_msg": message.reply_to_message
    }
    await message.reply_text(
        "📝 Send your custom caption template.\n\n"
        "Example:\n"
        "`{file_name}`\n\n"
        "File Name - `{file_name}`\n"
        "File Caption - `{file_caption}`\n"
        "Size - `{file_size}`\n"
        "File Audio - `{audio}`\n"
        "File Quality - `{quality}`\n"
        "File Years - `{Years}`\n"
        "File duration- `{duration}`\n"
        "Subtitles - `{subtitles}`\n"
        "Season - `{season}`\n"
        "Episode - `{episode}`\n"
        "Episode Name - `{episode_name}`\n\n"
        "/cancel - Cancel this process",
        quote=True
    )

@Client.on_message(filters.text & ~filters.command(["change_caption", "set_template", "del_template", "cancel", "my_template"]))
async def receive_template(client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text.lower() == "/cancel":
        if user_id in pending_caption:
            pending_caption.pop(user_id)
            await message.reply_text("❌ Caption change process cancelled.")
        else:
            await message.reply_text("No active process to cancel.")
        return

    if user_id in pending_caption:
        data = pending_caption.pop(user_id)
        file_info = data["file_info"]
        new_caption = format_caption(text, file_info)
        await message.reply_video(
            video=data["file_id"],
            caption=new_caption
        )
        if AUTO_DELETE_OLD:
            await data["old_msg"].delete()

@Client.on_message(filters.command("set_template"))
async def set_template_cmd(client, message: Message):
    template = message.text.replace("/set_template", "", 1).strip()
    if not template:
        return await message.reply_text("❌ Please provide a template after the command.")

    templates_col.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"template": template}},
        upsert=True
    )
    await message.reply_text("✅ Permanent caption template saved!")

@Client.on_message(filters.command("del_template"))
async def del_template_cmd(client, message: Message):
    result = templates_col.delete_one({"user_id": message.from_user.id})
    if result.deleted_count:
        await message.reply_text("✅ Your permanent template has been deleted.")
    else:
        await message.reply_text("❌ You don't have a saved template.")

@Client.on_message(filters.command("my_template"))
async def my_template_cmd(client, message: Message):
    saved_template = templates_col.find_one({"user_id": message.from_user.id})
    if saved_template and "template" in saved_template:
        await message.reply_text(
            f"📝 **Your current saved template:**\n\n`{saved_template['template']}`",
            quote=True
        )
    else:
        await message.reply_text("❌ You don't have a saved template.")
