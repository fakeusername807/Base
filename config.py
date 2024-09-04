# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr

import re, os, time
id_pattern = re.compile(r'^.\d+$') 

class Rkn_Bots(object):
    
    # Rkn client config  ( required.. 😥)
    API_ID = os.environ.get("API_ID", "25492855")
    API_HASH = os.environ.get("API_HASH", "61876db014de51a4ace6b169608be4f1")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

    # start_pic
    RKN_PIC = os.environ.get("RKN_PIC", "https://graph.org/file/c748879538a3c96b10696.jpg")

    # wes response configuration
    BOT_UPTIME = time.time()
    PORT = int(os.environ.get("PORT", "8080"))

    # force subs channel ( required.. 😥)
    FORCE_SUB = os.environ.get("FORCE_SUB", "hgbot") 
    
    # database config ( required.. 😥)
    DB_NAME = os.environ.get("DB_NAME", "HGBOTZ")     
    DB_URL = os.environ.get("DB_URL", "")

    # default caption 
    DEF_CAP = os.environ.get("DEF_CAP", "{file_name}")

    # sticker Id
    STICKER_ID = os.environ.get("STICKER_ID", "CAACAgIAAxkBAAELFqBllhB70i13m-woXeIWDXU6BD2j7wAC9gcAAkb7rAR7xdjVOS5ziTQE")

    # admin id  ( required.. 😥)
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6359874284').split()]
    

# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr
