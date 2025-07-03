


from aiohttp import web
from pyrogram import Client
from config import HgBotz, HgBotz as HGBOT 
from HgBotz.web_support import web_server

class HgBotz(Client):
    def __init__(self):
        super().__init__(
            name="HgBotz",
            api_id=HGBOT.API_ID,
            api_hash=HGBOT.API_HASH,
            bot_token=HGBOT.BOT_TOKEN,
            workers=200,
            plugins={"root": "HgBotz"},
            sleep_threshold=15,
        )

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.uptime = HGBOT.BOT_UPTIME
        self.force_channel = HGBOT.FORCE_SUB
        if HGBOT.FORCE_SUB:
            try:
                link = await self.export_chat_invite_link(HGBOT.FORCE_SUB)
                self.invitelink = link
            except Exception as e:
                print(e)
                print("Make Sure Bot admin in force sub channel")
                self.force_channel = None
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, HGBOT.PORT).start()
        print(f"{me.first_name} Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️")
        for id in HGBOT.ADMIN:
            try:
                await self.send_message(id, f"**__{me.first_name}  Iꜱ Sᴛᴀʀᴛᴇᴅ.....✨️__**")
            except:
                pass
        
    async def stop(self, *args):
        await super().stop()
        print("Bot Stopped 🙄")
        
HgBotz().run()
