# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os

# Login feature, if you want then True , if you don't want then False
LOGIN_SYSTEM = bool(os.environ.get('LOGIN_SYSTEM', True)) # True or False

if LOGIN_SYSTEM == False:
    # if login system is False then fill your tg account session below 
    STRING_SESSION = os.environ.get("STRING_SESSION", "")
else:
    STRING_SESSION = None

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "33361737"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "7cd3bda26b08957a7205bbe8a51e6e90")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "8391386178"))

# Auto delete time seconds mein (5 minutes = 300 seconds)
AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", 300))

# 🎫 TOKEN VERIFICATION SYSTEM SYSTEM (ULTRA PREMIUM)
TOKEN_TIMEOUT = 86400  # Seconds mein timing set karein (1 hr = 3600, 12 hr = 43200, 24 hr = 86400)
SHORTENER_URL = "vplink.in"  # Apni website ka shortener domain bina https:// ke
SHORTENER_API = "643cf7208bfdc009d2e1f953905840a9619d48ca"  # Apni shortener website ka API KEY dalein

# 📊 LOG CHANNEL SYSTEM
LOG_CHANNEL = -1004214402860  # Apna Log Channel ID yahan dalein

# Your Channel Id In Which Bot Upload Downloaded Video/File/Message etc.
# And Make Your Bot Admin In this channel with full rights.
# if you don't want to upload in channel then leave it blank don't fill anything.
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")


CHANNEL_ID = -1003985895823  # Aapki normal channel ID
# Link automatic button par lag jayegi

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "mongodb+srv://gxmon239:f4l7bKrhka3Fh2cV@cluster0.qmblwql.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "vjsavecontentbot")

# Increase time as much as possible to avoid floodwait, spamming and tg account ban issues.
WAITING_TIME = int(os.environ.get("WAITING_TIME", "10")) # time in seconds

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
