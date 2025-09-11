import re, time, os
from os import environ


id_pattern = re.compile(r'^.\d+$')

AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('AUTH_CHANNEL', '0').split()] # give channel id with seperate space. Ex : ('-10073828 -102782829 -1007282828')

class HgBotz(object):
    
    
    API_ID = os.environ.get("API_ID", "26334970")
    API_HASH = os.environ.get("API_HASH", "e7d1141cca9fbe1ab45804163b5080c8")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7928207862:AAFUk521pf1mHSGUxNf7WOxSm9NSJAR6w98")


    # wes response configuration
    BOT_UPTIME = time.time()
    PORT = int(os.environ.get("PORT", "8080"))

    # force subs channel ( required.. 😥)
    FORCE_SUB = os.environ.get("FORCE_SUB", "MrSagarbots") 
    
    # database config ( required.. 😥)
    DB_NAME = os.environ.get("DB_NAME", "MrSagarbots")     
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://testposter:testposter@cluster0.xhvxsol.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")


    # admin id  ( required.. 😥)
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '7965786027').split()]
