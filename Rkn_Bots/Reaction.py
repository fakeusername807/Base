import requests
from pyrogram import Client, filters, errors, types
from config import Rkn_Bots, AUTH_CHANNEL
import asyncio, re, time, sys, random
from .database import total_user, getid, delete, addCap, updateCap, insert, chnl_ids
from pyrogram.errors import *
from pyrogram.types import *
from utils import react_msg 
from Script import script
import aiohttp

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
        InlineKeyboardButton('❗️ʜᴇʟᴘ', callback_data='help'), 
        InlineKeyboardButton('🦋 𝙷𝙾𝙼𝙴', callback_data='back')
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

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN)  & filters.command(["stats"]))
async def all_db_users_here(client, message):
    start_t = time.time()
    rkn = await message.reply_text("Processing...")
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - client.uptime))    
    total_users = await total_user()
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rkn.edit(text=f"**--Bot Processed--** \n\n**Bot Started UpTime:** {uptime} \n**Bot Current Ping:** `{time_taken_s:.3f} ᴍꜱ` \n**All Bot Users:** `{total_users}`")


@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["broadcast"]))
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
@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(b, m):
    rkn_msg = await b.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=m.chat.id)       
    await asyncio.sleep(3)
    await rkn_msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)
    
NOTIFICATION_CHANNEL_ID = -1002346166150
@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    client = bot
    if AUTH_CHANNEL:
        try:
            btn = await is_subscribed(client, message, AUTH_CHANNEL)
            if btn:
                username = (await client.get_me()).username
                if message.command:
                    btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")])
                else:
                    btn.append([InlineKeyboardButton("♻️ Try Again ♻️", url=f"https://t.me/{username}?start=true")])
                await message.reply_text(text=f"<b>👋 Hello {message.from_user.mention},\n\nPlease join the channel then click on try again button. 😇</b>", reply_markup=InlineKeyboardMarkup(btn))
                return
        except Exception as e:
            print(e)
    user_id = int(message.from_user.id)
    reply_markup=InlineKeyboardMarkup(buttons)
    await insert(user_id)
    notification_text = f"🎉 New user started the bot: {message.from_user.mention} (ID: {user_id})"
    await bot.send_message(NOTIFICATION_CHANNEL_ID, notification_text)
    await message.reply_photo(photo=Rkn_Bots.RKN_PIC,
        caption=script.START_TXT.format(message.from_user.mention),
        has_spoiler=True, 
        reply_markup=reply_markup)

@Client.on_message(filters.command("start") & filters.group)
async def group_start_cmd(bot, message):
    await react_msg(bot, message)
    user_id = int(message.from_user.id)
    reply_markup=InlineKeyboardMarkup(group_buttons)
    await insert(user_id)
    await message.reply_text(text=script.START_TXT.format(message.from_user.mention),
        message_effect_id = 5044134455711629726, 
        reply_markup=reply_markup)


#----------------------Fin.py - - - - - - - - - - - - - - - - 

@Client.on_message(filters.command("dice"))
async def roll_dice(bot, message):
    await bot.send_dice(message.chat.id, "🎲")


@Client.on_message(filters.command("arrow"))                                      
async def roll_arrow(bot, message):
    await bot.send_dice(message.chat.id, "🎯")

@Client.on_message(filters.command("goal"))
async def roll_goal(bot, message):
    await bot.send_dice(message.chat.id, "⚽️")

@Client.on_message(filters.command("luck"))
async def roll_luck(bot, message):
    await bot.send_dice(message.chat.id, "🎰")

@Client.on_message(filters.command("throw"))
async def roll_throw(bot, message):
    await bot.send_dice(message.chat.id, "🏀")

@Client.on_message(filters.command(["bowling", "tenpins"]))
async def roll_bowling(bot, message):
    await bot.send_dice(message.chat.id, "🎳")


@Client.on_callback_query(filters.regex('help'))
async def show_help_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()  # Acknowledge the callback
    await callback_query.message.edit_text(text=script.HELP_TXT, reply_markup=InlineKeyboardMarkup(back_button))

@Client.on_callback_query(filters.regex('back'))
async def back_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()  # Acknowledge the callback
    await callback_query.message.edit_text(text=script.HOME_TXT, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex('about'))
async def about_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()# Acknowledge the callback
    await callback_query.message.edit_text(text=script.ABOUT_TXT, reply_markup=InlineKeyboardMarkup(about_buttons))

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["msg"]))
async def send_message_to_channel(bot, message):
    # Check if the command is used correctly
    if len(message.command) < 4:
        await message.reply_text("**Usage:** /msg <channel_id> <loop_time> <message>")
        return

    # Extract channel ID, loop time, and message from the command
    channel_id = message.command[1]
    loop_time = int(message.command[2])  # Number of times to send the message
    msg_text = " ".join(message.command[3:])  # The message to send

    try:
        # Loop and send the message
        for i in range(loop_time):
            await bot.send_message(int(channel_id), msg_text)
            await asyncio.sleep(1)  # Add a small delay to avoid spamming
        await message.reply_text(f"Message sent {loop_time} times to channel/group {channel_id}!")
    except Exception as e:
        await message.reply_text(f"Failed to send message to channel/group {channel_id}. Error: {str(e)}")



@Client.on_message(filters.command("poster") & filters.all)
async def poster_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Please provide a movie name.\nUsage: `/poster Animal`", parse_mode="Markdown")

    query = " ".join(message.command[1:])
    api_url = f"http://hgbotz.serv00.net/tmdb/api.php?query={query}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                return await message.reply("Failed to fetch data.")
            data = await resp.json()

    poster = data["posters"][0] if data.get("posters") else "N/A"
    english = "\n".join(data.get("english_backdrops", [])) or "N/A"
    hindi = "\n".join(data.get("hindi_backdrops", [])) or "N/A"

    text = f"<b>Movie:</b> <code>{query}</code>\n\n"
    text += f"<b>Poster URL:</b>\n<code>{poster}</code>\n\n"
    text += f"<b>English Backdrops:</b>\n<code>{english}</code>\n\n"
    text += f"<b>Hindi Backdrops:</b>\n<code>{hindi}</code>"

    await message.reply(text, disable_web_page_preview=True)
#--------- react.py-------

@Client.on_message(filters.all)
async def send_reaction(bot, message):
    await react_msg(bot, message)
