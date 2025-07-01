

import re, time, os
from os import environ


id_pattern = re.compile(r'^.\d+$')

AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('AUTH_CHANNEL', '-1002166149059').split()] # give channel id with seperate space. Ex : ('-10073828 -102782829 -1007282828')

class HgBotz(object):
    
    
    API_ID = os.environ.get("API_ID", "25492855")
    API_HASH = os.environ.get("API_HASH", "61876db014de51a4ace6b169608be4f1")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7999210242:AAE2cNUSIbubvCHY1Uy6LslOsLT2rcD4Mpk")


    # wes response configuration
    BOT_UPTIME = time.time()
    PORT = int(os.environ.get("PORT", "8080"))

    # force subs channel ( required.. 😥)
    FORCE_SUB = os.environ.get("FORCE_SUB", "hgbotz") 
    
    # database config ( required.. 😥)
    DB_NAME = os.environ.get("DB_NAME", "Postersbot")     
    DB_URL = os.environ.get("DB_URL", "mongodb+srv://harsh:gunnu@cluster0.0uqkd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")


    # admin id  ( required.. 😥)
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6359874284').split()]
    
