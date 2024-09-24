# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr

from pyrogram import Client, filters, errors, types
from config import Rkn_Bots
import asyncio, re, time, sys
from .database import total_user, getid, delete, addCap, updateCap, insert, chnl_ids
from pyrogram.errors import FloodWait
from pyrogram.types import *
from utils import react_msg 

buttons = [[
        InlineKeyboardButton('✇ Uᴘᴅᴀᴛᴇs ✇', url="https://t.me/HGBOTZ"),
        InlineKeyboardButton('✨ 𝙲𝙾𝙽𝚃𝙰𝙲𝚃 ✨', url="https://t.me/Harshit_contact_bot")
    ],[
        InlineKeyboardButton('〄 Add to me group 〄', url="https://t.me/Reaction_99bot?startgroup=botstart")
    ]]

group_buttons = [[InlineKeyboardButton('✇ Uᴘᴅᴀᴛᴇs ✇', url="https://t.me/HGBOTZ")]] 

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
    
@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    await react_msg(bot, message)
    user_id = int(message.from_user.id)
    reply_markup=InlineKeyboardMarkup(buttons)
    await insert(user_id)
    await message.reply_photo(photo=Rkn_Bots.RKN_PIC,
        caption=f"<b>Hᴇʟʟᴏ 😎 {message.from_user.mention} ✨</b>\n<b><blockquote>ɪ ᴀᴍ SIMPEL 😁 BUT ᴘᴏᴡᴇʀꜰᴜʟʟ AUTO REACTION ʙᴏᴛ ᴊᴜꜱᴛ Make Admin in Your Grouo/Chat to see Magic☜ </blockquote><b>\n\n<b><spoiler>🔋Maintained by <a href='https://t.me/Harshit_contact_bot'>ℍ𝕒ℝ𝕤ℍ𝕚𝕋</a></spoiler><b>",
        has_spoiler=True, 
        reply_markup=reply_markup)

@Client.on_message(filters.command("start") & filters.group)
async def start_cmd(bot, message):
    await react_msg(bot, message)
    user_id = int(message.from_user.id)
    reply_markup=InlineKeyboardMarkup(group_buttons)
    await insert(user_id)
    await message.reply_text(text=f"<b>Hᴇʟʟᴏ 😎 {message.from_user.mention} ✨</b>\n<b><blockquote>ɪ ᴀᴍ SIMPEL 😁 BUT ᴘᴏᴡᴇʀꜰᴜʟʟ AUTO REACTION ʙᴏᴛ ᴊᴜꜱᴛ Make Admin in Your Grouo/Chat to see Magic☜ </blockquote><b>\n<b><spoiler>🔋Maintained by <a href='https://t.me/Harshit_contact_bot'>ℍ𝕒ℝ𝕤ℍ𝕚𝕋</a></spoiler><b>",
        reply_markup=reply_markup)

@Client.on_message(filters.all)
async def send_reaction(bot, message):
    await react_msg(bot, message)
