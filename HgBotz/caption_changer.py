from pyrogram import Client, filters
from pyrogram.types import Message
import re
import os
import requests
from pymongo import MongoClient
from config import HgBotz

# TMDB API key directly from environment
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "fe6745c215b5ed09da847340eae06b9e")

# MongoDB setup
mongo_client = MongoClient(HgBotz.DB_URL)
db = mongo_client[HgBotz.DB_NAME]
templates_col = db["caption_templates"]

# Config
AUTO_DELETE_OLD = False  # Set False if you want to keep old video messages

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

    # Extract possible show name
    show_name = re.split(r'[Ss]\d{1,2}[Ee]\d{1,2}', file_name)[0].replace('.', ' ').strip()
    if not show_name:
        return "Unknown"

    try:
        # Search TMDB for the show
        search_url = "https://api.themoviedb.org/3/search/tv"
        params = {"api_key": TMDB_API_KEY, "query": show_name}
        resp = requests.get(search_url, params=params, timeout=10).json()
        if not resp.get("results"):
            return "Unknown"

        show_id = resp["results"][0]["id"]

        # Get episode details
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

    # Year detection
    year_match = re.search(r'(19\d{2}|20\d{2})', file_name)
    year = year_match.group(1) if year_match else "Unknown"

    # Language detection
    langs = []
    for lang in ["Hindi", "English", "Tamil", "Telugu", "Malayalam", "Kannada", "Bengali", "Bangla", "Punjabi", "Gujarati", "Marathi"]:
        if re.search(lang, file_name, re.IGNORECASE) or re.search(lang, caption, re.IGNORECASE):
            langs.append(lang)
    audio_langs = ", ".join(langs) if langs else "Unknown"

    # Subtitles detection
    subs_match = re.findall(r'([a-zA-Z]+)(?=\s*sub)', file_name + " " + caption, re.IGNORECASE)
    subtitles = ", ".join(set([s.title() for s in subs_match])) if subs_match else "None"

    # Season detection
    season_match = re.search(r'[Ss](\d{1,2})', file_name)
    season = f"S{season_match.group(1).zfill(2)}" if season_match else "Unknown"

    # Episode detection
    episode_match = re.search(r'[Ee](\d{1,2})', file_name)
    episode = f"E{episode_match.group(1).zfill(2)}" if episode_match else "Unknown"

    # TMDB Episode Name
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

# In-memory for ongoing sessions
pending_caption = {}

@Client.on_message(filters.command("change_caption") & filters.group)
async def change_caption_cmd(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.video:
        return await message.reply_text("❌ Please reply to a video file.")

    file_info = extract_file_info(message.reply_to_message)
    user_id = message.from_user.id

    # Check if user has a saved template in Mongo
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

    # No saved template — ask for one
    pending_caption[user_id] = {
        "file_info": file_info,
        "file_id": message.reply_to_message.video.file_id,
        "old_msg": message.reply_to_message
    }
    await message.reply_text(
        "📝 Send your custom caption template.\n\n"
        "Example:\n"
        "`{file_name}`\n\n"
        "𝖩𝗈𝗂𝗇 ➥ 「 @Mrsagarbots 」\n\n"
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

@Client.on_message(filters.text & ~filters.command(["change_caption", "set_template", "del_template", "my_template", "cancel"]))
async def receive_template(client, message):
    user_id = message.from_user.id
    text = message.text.strip()

    # Cancel process
    if text.lower() == "/cancel":
        if user_id in pending_caption:
            pending_caption.pop(user_id)
            await message.reply_text("❌ Caption change process cancelled.")
        else:
            await message.reply_text("No active process to cancel.")
        return

    # Process pending caption
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

@Client.on_message(filters.command("set_template") & filters.group)
async def set_template_cmd(client, message):
    template = message.text.replace("/set_template", "", 1).strip()
    if not template:
        return await message.reply_text("❌ Please provide a template after the command.")

    templates_col.update_one(
        {"user_id": message.from_user.id},
        {"$set": {"template": template}},
        upsert=True
    )
    await message.reply_text("✅ Permanent caption template saved!")

@Client.on_message(filters.command("del_template") & filters.group)
async def del_template_cmd(client: Client, message: Message):
    result = templates_col.delete_one({"user_id": message.from_user.id})
    if result.deleted_count:
        await message.reply_text("✅ Your permanent template has been deleted.")
    else:
        await message.reply_text("❌ You don't have a saved template.")

@Client.on_message(filters.command("my_template") & filters.group)
async def my_template_cmd(client, message):
    saved_template = templates_col.find_one({"user_id": message.from_user.id})
    if saved_template and "template" in saved_template:
        await message.reply_text(
            f"📝 **Your current saved template:**\n\n`{saved_template['template']}`",
            quote=True
        )
    else:
        await message.reply_text("❌ You don't have a saved template.")
