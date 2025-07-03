import requests
from pyrogram import Client, filters, errors, types
from config import HgBotz, AUTH_CHANNEL
import asyncio, re, time, sys, random
from .database import total_user, getid, delete insert
from pyrogram.errors import *
from pyrogram.types import *
from Script import script
import aiohttp
import openai
from datetime import datetime 

buttons = [[
        InlineKeyboardButton('✇ Uᴘᴅᴀᴛᴇs ✇', url="https://t.me/HGBOTZ"),
        InlineKeyboardButton('✨ 𝙲𝙾𝙽𝚃𝙰𝙲𝚃 ✨', url="https://t.me/Harshit_contact_bot")
    ],[
        InlineKeyboardButton('〄 Add to me group 〄', url="https://t.me/Reaction_99bot?startgroup=botstart")
    ],[
        InlineKeyboardButton('ˣ 𝙰𝙳𝙳 𝙼𝙴 𝚃𝙾 𝚈𝙾𝚄𝚁 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 ˣ', url='https://t.me/Reaction_99bot?startchannel&admin=post_messages+edit_messages+delete_messages'),
    ],[
        InlineKeyboardButton('❗️ʜᴇʟᴘ', callback_data='help'), 
        InlineKeyboardButton('🦋 𝙰𝙱𝙾𝚄𝚃', callback_data='about')
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

about_buttons = [[
        InlineKeyboardButton('🙂 𝐎𝐖𝐍𝐄𝐑', url='https://t.me/Harshit_contact_bot')
       ],[
        InlineKeyboardButton('📜 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/HGBOTZ_support'),
        InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://telegram.me/hgbotz')
        ]]


async def is_subscribed(bot, query, channel):
    btn = []
    for id in channel:
        chat = await bot.get_chat(int(id))
        try:
            await bot.get_chat_member(id, query.from_user.id)
        except UserNotParticipant:
            btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
        except Exception as e:
            pass
    return btn

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
    



openai.api_key = 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



# In-memory storage for user states
user_states = {}

@Client.on_message(filters.command(["start", "help"]))
async def start_command(client, message: Message):
    await message.reply_text(
        "✨ Welcome to Cosmic Insights Bot! ✨\n\n"
        "Get personalized astrology reports based on your birth details.\n\n"
        "To begin, use:\n/horoscope\n\n"
        "Need help? Contact @YourSupport"
    )

@Client.on_message(filters.command("horoscope"))
async def horoscope_command(client, message: Message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_date"
    
    await message.reply_text(
        "🌌 Let's explore your cosmic blueprint! 🌌\n\n"
        "Please send your birth date in DD/MM/YYYY format:\n"
        "Example: 15/08/1990"
    )

@Client.on_message(filters.private & filters.text)
async def handle_messages(client, message: Message):
    user_id = message.from_user.id
    current_state = user_states.get(user_id)

    if not current_state:
        return

    text = message.text.strip()

    try:
        if current_state == "waiting_date":
            # Validate date format
            if not re.match(r"^\d{2}/\d{2}/\d{4}$", text):
                raise ValueError("Invalid format. Use DD/MM/YYYY")
                
            datetime.strptime(text, "%d/%m/%Y")
            user_states[user_id] = {"date": text, "state": "waiting_time"}
            
            await message.reply_text(
                "⏱ Great! Now send your birth time (24-hour format):\n"
                "Example: 14:30"
            )
            
        elif current_state["state"] == "waiting_time":
            # Validate time format
            if not re.match(r"^\d{1,2}:\d{2}$", text):
                raise ValueError("Invalid format. Use HH:MM")
                
            time_parts = text.split(":")
            if not (0 <= int(time_parts[0]) <= 23 and 0 <= int(time_parts[1]) <= 59):
                raise ValueError("Invalid time. Hours: 0-23, Minutes: 0-59")
                
            user_states[user_id]["time"] = text
            user_states[user_id]["state"] = "waiting_place"
            
            await message.reply_text(
                "📍 Now send your birth place (City, Country):\n"
                "Example: Mumbai, India"
            )
            
        elif current_state["state"] == "waiting_place":
            if len(text) < 3:
                raise ValueError("Place name too short")
                
            birth_details = user_states[user_id]
            del user_states[user_id]  # Clear user state
            
            # Show processing message
            processing = await message.reply_text(
                "🔮 Calculating your cosmic blueprint...\n"
                "This may take 20-30 seconds..."
            )
            
            # Generate astrology report
            report = await generate_astrology_report(
                birth_details["date"],
                birth_details["time"],
                text
            )
            
            # Send results
            await processing.delete()
            await message.reply_text(
                f"🌟 **Your Cosmic Insights Report** 🌟\n\n"
                f"**Birth Details:**\n"
                f"Date: {birth_details['date']}\n"
                f"Time: {birth_details['time']}\n"
                f"Place: {text}\n\n"
                f"{report}",
                parse_mode="markdown"
            )
            
    except ValueError as e:
        await message.reply_text(f"❌ Error: {str(e)}\nPlease try again.")
    except Exception as e:
        await message.reply_text(f"🚨 System error: {str(e)}\nPlease try /horoscope again")
        if user_id in user_states:
            del user_states[user_id]

async def generate_astrology_report(date: str, time: str, place: str) -> str:
    """Generate astrology report using ChatGPT API"""
    prompt = (
        f"Act as a professional astrologer. Generate a detailed astrology report based on these birth details:\n"
        f"- Date: {date}\n"
        f"- Time: {time}\n"
        f"- Place: {place}\n\n"
        "Include these sections:\n"
        "1. Sun Sign and Key Characteristics\n"
        "2. Moon Sign and Emotional Nature\n"
        "3. Ascendant/Rising Sign\n"
        "4. Planetary Dominants\n"
        "5. Life Path Insights\n"
        "6. Current Cosmic Influences\n\n"
        "Use Western astrology system. Provide 4-5 paragraphs of insightful, personalized interpretation."
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert astrologer with 30 years of experience."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7,
    )
    
    return response.choices[0].message['content'].strip()

