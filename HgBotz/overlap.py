from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from PIL import Image
import aiohttp
import io



# In-memory store (user_id: {jpg, png, scale})
pending = {}

try:
    resample_method = Image.Resampling.LANCZOS
except AttributeError:
    resample_method = Image.ANTIALIAS

async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return Image.open(io.BytesIO(await resp.read())).convert("RGBA")
            return None

# Inline keyboard for position selection
def position_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("↖ Top Left", callback_data="overlap_pos_top_left"),
            InlineKeyboardButton("🔝 Top", callback_data="overlap_pos_top"),
            InlineKeyboardButton("↗ Top Right", callback_data="overlap_pos_top_right")
        ],
        [
            InlineKeyboardButton("◀ Middle Left", callback_data="overlap_pos_middle_left"),
            InlineKeyboardButton("🎯 Center", callback_data="overlap_pos_middle"),
            InlineKeyboardButton("▶ Middle Right", callback_data="overlap_pos_middle_right")
        ],
        [
            InlineKeyboardButton("↙ Bottom Left", callback_data="overlap_pos_bottom_left"),
            InlineKeyboardButton("🔚 Bottom", callback_data="overlap_pos_bottom"),
            InlineKeyboardButton("↘ Bottom Right", callback_data="overlap_pos_bottom_right")
        ]
    ])

# /overlap command
@Client.on_message(filters.command("overlap") & filters.all)
async def overlap_handler(_, message: Message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            return await message.reply("❗ Usage:\n`/overlap jpg_url png_url [scale_percent]`")

        jpg_url = parts[1]
        png_url = parts[2]
        scale_percent = int(parts[3]) if len(parts) >= 4 and parts[3].isdigit() else 50

        if not (5 <= scale_percent <= 100):
            return await message.reply("⚠️ Scale must be between 5 and 100.")

        pending[message.from_user.id] = {
            "jpg_url": jpg_url,
            "png_url": png_url,
            "scale": scale_percent
        }

        await message.reply("📍 Choose overlay position:", reply_markup=position_keyboard())

    except Exception as e:
        await message.reply(f"❌ Error: `{e}`")

# Callback for position selection
@Client.on_callback_query(filters.regex(r"^overlap_pos_"))
async def handle_position(_, query: CallbackQuery):
    try:
        await query.answer()
        user_id = query.from_user.id

        if user_id not in pending:
            return await query.message.edit("❌ Session expired or not found.")

        # Extract position
        pos = query.data.replace("overlap_pos_", "")
        data = pending.pop(user_id)
        jpg_url, png_url, scale = data["jpg_url"], data["png_url"], data["scale"]

        status = await query.message.edit("🔄 Processing image...")

        base_image = await fetch_image(jpg_url)
        overlay_image = await fetch_image(png_url)

        if not base_image or not overlay_image:
            return await status.edit("❌ Failed to fetch one or both images.")

        base_image = base_image.convert("RGBA")
        overlay_image = overlay_image.convert("RGBA")

        # Resize overlay
        target_width = int((scale / 100) * base_image.width)
        aspect_ratio = overlay_image.height / overlay_image.width
        target_height = int(target_width * aspect_ratio)
        overlay_image = overlay_image.resize((target_width, target_height), resample_method)

        # Position calculation
        positions = {
            "top_left": (0, 0),
            "top": ((base_image.width - overlay_image.width) // 2, 0),
            "top_right": (base_image.width - overlay_image.width, 0),
            "middle_left": (0, (base_image.height - overlay_image.height) // 2),
            "middle": ((base_image.width - overlay_image.width) // 2, (base_image.height - overlay_image.height) // 2),
            "middle_right": (base_image.width - overlay_image.width, (base_image.height - overlay_image.height) // 2),
            "bottom_left": (0, base_image.height - overlay_image.height),
            "bottom": ((base_image.width - overlay_image.width) // 2, base_image.height - overlay_image.height),
            "bottom_right": (base_image.width - overlay_image.width, base_image.height - overlay_image.height),
        }

        x, y = positions.get(pos, positions["middle"])  # Fallback to center

        combined = base_image.copy()
        combined.paste(overlay_image, (x, y), overlay_image)

        output = io.BytesIO()
        output.name = "merged.jpg"
        combined.convert("RGB").save(output, "JPEG", quality=95)
        output.seek(0)

        await query.message.reply_photo(photo=output, caption=f"✅ Overlay: {pos.replace('_', ' ').title()} ({scale}%)")
        await status.delete()

    except Exception as e:
        await query.message.edit(f"❌ Error: `{e}`")
