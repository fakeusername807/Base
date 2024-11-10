# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr

import re, time, os
from os import environ

id_pattern = re.compile(r'^.\d+$')

AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('AUTH_CHANNEL', '').split()] # give channel id with seperate space. Ex : ('-10073828 -102782829 -1007282828')

class Rkn_Bots(object):
    
    # Rkn client config  ( required.. 😥)
    API_ID = os.environ.get("API_ID", "25492855")
    API_HASH = os.environ.get("API_HASH", "61876db014de51a4ace6b169608be4f1")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7080367896:AAG2YkXiDMwNzeANmHYoG-nSUTNFdIfWcL4")

    # start_pic
    RKN_PIC = os.environ.get("RKN_PIC", "https://graph.org/file/8487c51d55be5b4e17222.jpg")

    # wes response configuration
    BOT_UPTIME = time.time()
    PORT = int(os.environ.get("PORT", "8080"))

    # force subs channel ( required.. 😥)
    FORCE_SUB = os.environ.get("FORCE_SUB", "hgbotz") 
    
    # database config ( required.. 😥)
    DB_NAME = os.environ.get("DB_NAME", "HGBOTZ")     
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://david:Nath@cluster0.dv0ma.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

    # default caption 
    DEF_CAP = os.environ.get("DEF_CAP", "{filename}")

    # sticker Id
    STICKER_ID = os.environ.get("STICKER_ID", "CAACAgIAAxkBAAELFqBllhB70i13m-woXeIWDXU6BD2j7wAC9gcAAkb7rAR7xdjVOS5ziTQE")

    # admin id  ( required.. 😥)
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6359874284').split()]
    

# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr
