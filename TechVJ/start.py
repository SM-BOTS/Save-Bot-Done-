# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import time
import string
import random
import aiohttp
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME, AUTO_DELETE_TIME, TOKEN_TIMEOUT, SHORTENER_URL, SHORTENER_API, LOG_CHANNEL
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser

class batch_temp(object):
    IS_BATCH = {}

USER_STATES = {}

# Helper function: Short link banane ke liye aur unique token generator (FIXED)
async def get_short_link(client, user_id, token):
    bot_username = (await client.get_me()).username
    long_url = f"https://t.me/{bot_username}?start=verify_{user_id}_{token}"
    api_url = f"https://{SHORTENER_URL}/api?api={SHORTENER_API}&url={long_url}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                data = await response.json()
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
    except Exception as e:
        print(f"Shortener API Error: {e}")
    return long_url

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile): break
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread: txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except: await asyncio.sleep(5)

async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile): break
        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread: txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except: await asyncio.sleep(5)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

async def auto_delete_worker(messages, delay):
    await asyncio.sleep(delay)
    for msg in messages:
        try: await msg.delete()
        except: pass

# start command (With Token Verification & One-Time Use Validation)
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"
    
    # Check if New User for Log Channel Tracking
    is_new = not await db.is_user_exist(user_id)
    if is_new:
        await db.add_user(user_id, first_name)
        if LOG_CHANNEL:
            log_text = (
                "🎯 **⚡ NEW USER NOTIFICATION ⚡**\n\n"
                f"👤 **Name:** {message.from_user.mention}\n"
                f"🆔 **User ID:** `{user_id}`\n"
                f"🌐 **Username:** {username}\n"
                f"📅 **Joined On:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                "───────────────────────"
            )
            try:
                await client.send_message(chat_id=LOG_CHANNEL, text=log_text, parse_mode=enums.ParseMode.HTML)
            except Exception as le:
                print(f"Log Channel Error: {le}")

    # Handling verification callback payload from shortener link
    if len(message.text.split()) > 1:
        payload = message.text.split()[1]
        if payload.startswith("verify_"):
            try:
                _, p_user_id, p_token = payload.split("_")
                if int(p_user_id) == user_id:
                    # ONE-TIME USE CHECK: Database se token validation checking
                    db_token = await db.get_verification_token(user_id)
                    if db_token and db_token == p_token:
                        await db.update_verify_status(user_id) # Token verified and instantly deleted from DB
                        await message.reply_text("✅ **Aapka Token Successfully Verify Ho Gaya Hai!**\n\nAb aap bot ko unlimited use kar sakte hain.")
                        return
                    else:
                        await message.reply_text("❌ **Verification Link Expired!** Yeh link ek baar use ho chuki hai ya purani hai. Kripya naya link generate karein.")
                        return
                else:
                    await message.reply_text("❌ **Security Alert:** Yeh verification link aapke account ke liye nahi hai.")
                    return
            except Exception as err:
                await message.reply_text(f"❌ Verification processing error: {err}")
                return

    # Normal Panel Show System
    buttons = [[
        InlineKeyboardButton("⚙️ Settings", callback_data="open_settings")
    ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/vj_bot_disscussion'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/vj_bots')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help</b>", 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id
    )
    return

# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(chat_id=message.chat.id, text=f"{HELP_TXT}")

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(chat_id=message.chat.id, text="**Batch Successfully Cancelled.**")

# ========================================================
# ⚙️ SETTINGS SYSTEM WITH CALLBACK HANDLERS
# ========================================================
@Client.on_message(filters.command(["settings"]) & filters.private)
async def settings_cmd(client: Client, message: Message):
    user_id = message.from_user.id
    dump_id = await db.get_dump_id(user_id)
    caption = await db.get_caption(user_id)
    dump_status = f"`{dump_id}`" if dump_id else "❌ Not Set"
    cap_status = "✅ Set" if caption else "❌ Not Set"
    
    text = f"**⚙️ BOT SETTINGS PANEL**\n\n📁 **Dump Channel:** {dump_status}\n📝 **Custom Caption:** {cap_status}\n\nNiche diye gaye buttons se apni settings manage karein:"
    buttons = [
        [InlineKeyboardButton("📁 Set Dump", callback_data="set_dump"), InlineKeyboardButton("🗑️ Remove Dump", callback_data="rem_dump")],
        [InlineKeyboardButton("📝 Set Caption", callback_data="set_cap"), InlineKeyboardButton("🗑️ Remove Caption", callback_data="rem_cap")]
    ]
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query()
async def handle_callbacks(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    data = query.data
    
    if data == "open_settings":
        dump_id = await db.get_dump_id(user_id)
        caption = await db.get_caption(user_id)
        dump_status = f"`{dump_id}`" if dump_id else "❌ Not Set"
        cap_status = "✅ Set" if caption else "❌ Not Set"
        text = f"**⚙️ BOT SETTINGS PANEL**\n\n📁 **Dump Channel:** {dump_status}\n📝 **Custom Caption:** {cap_status}"
        buttons = [
            [InlineKeyboardButton("📁 Set Dump", callback_data="set_dump"), InlineKeyboardButton("🗑️ Remove Dump", callback_data="rem_dump")],
            [InlineKeyboardButton("📝 Set Caption", callback_data="set_cap"), InlineKeyboardButton("🗑️ Remove Caption", callback_data="rem_cap")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "set_dump":
        USER_STATES[user_id] = "waiting_for_dump"
        await query.message.edit_text("**📁 Apni Private Channel ki ID send karo:**\n\n_(Example: `-1001234567890`)_", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="open_settings")]]))
        
    elif data == "rem_dump":
        await db.remove_dump_id(user_id)
        await query.answer("📁 Dump Channel successfully hata diya!", show_alert=True)
        
    elif data == "set_cap":
        USER_STATES[user_id] = "waiting_for_caption"
        await query.message.edit_text("**📝 Apna naya Custom Caption send karo:**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="open_settings")]]))
        
    elif data == "rem_cap":
        await db.remove_caption(user_id)
        await query.answer("📝 Custom Caption successfully hata diya!", show_alert=True)

# ========================================================
# 💬 INCOMING MESSAGE TEXT & LINKS LOGIC (VERIFICATION CONTROL)
# ========================================================
@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    user_id = message.from_user.id

    if USER_STATES.get(user_id) == "waiting_for_dump":
        dump_id = message.text.strip()
        if dump_id.startswith("-100"):
            try:
                await db.set_dump_id(user_id, int(dump_id))
                USER_STATES.pop(user_id, None)
                await message.reply_text(f"✅ **Dump Channel ID Save:** `{dump_id}`")
            except: await message.reply_text("❌ **ID Error!** Numbers properly check karein.")
        else: await message.reply_text("❌ Channel ID hamesha `-100` se shuru honi chahiye.")
        return

    elif USER_STATES.get(user_id) == "waiting_for_caption":
        custom_caption = message.text
        await db.set_caption(user_id, custom_caption)
        USER_STATES.pop(user_id, None)
        await message.reply_text("✅ **Custom Caption Save Ho Gaya!**")
        return

    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            return await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
        try:
            try: await TechVJUser.join_chat(message.text)
            except Exception as e: return await client.send_message(message.chat.id, f"Error : {e}", reply_to_message_id=message.id)
            await client.send_message(message.chat.id, "Chat Joined", reply_to_message_id=message.id)
        except UserAlreadyParticipant: await client.send_message(message.chat.id, "Chat already Joined", reply_to_message_id=message.id)
        return
    
    if "https://t.me/" in message.text:
        # 🎫 ULTRA LEVEL VERIFICATION GATEKEEPER
        is_verified = await db.get_verify_status(user_id, TOKEN_TIMEOUT)
        if not is_verified:
            # Token logic generate unique strings for extreme safety encryption
            token = "".join(random.choices(string.ascii_letters + string.digits, k=10))
            await db.set_verification_token(user_id, token) # DB validation storage
            
            # API parsing short URL string builder (FIXED CALL WITH CLIENT)
            short_url = await get_short_link(client, user_id, token)
            
            verify_buttons = [[
                InlineKeyboardButton("🎫 Verify Token", url=short_url)
            ]]
            timeout_hours = int(TOKEN_TIMEOUT / 3600)
            await message.reply_text(
                f"⚠️ **Verification Required!**\n\nApna content download karne ke liye token verify karein.\n"
                f"⏱️ **Validity:** `{timeout_hours} Hours`\n\n"
                f"👉 Niche diye gaye button par click karke verify karein, link ek hi baar use ki ja sakti hai.",
                reply_markup=InlineKeyboardMarkup(verify_buttons)
            )
            return

        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try: toID = int(temp[1].strip())
        except: toID = fromID

        if LOGIN_SYSTEM == True:
            user_data = await db.get_session(message.from_user.id)
            if user_data is None: return await message.reply("**For Downloading Restricted Content You Have To /login First.**")
            api_id = int(await db.get_api_id(message.from_user.id))
            api_hash = await db.get_api_hash(message.from_user.id)
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
                await acc.connect()
            except: return await message.reply("**Your Login Session Expired. /logout and /login again.**")
        else:
            if TechVJUser is None: return await client.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
            acc = TechVJUser
				
        batch_temp.IS_BATCH[message.from_user.id] = False
        user_uploaded_videos = []
        
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try: await handle_private(client, acc, message, chatid, msgid, user_uploaded_videos)
                except Exception as e:
                    if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
            elif "https://t.me/b/" in message.text:
                pass
            
            else:
                username = datas[3]
                try: msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try: await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try: await handle_private(client, acc, message, username, msgid, user_uploaded_videos)               
                    except Exception as e:
                        if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            pass
            
        if user_uploaded_videos:
            notif_text = f"⏳ Aapki saari files upload ho gayi hain! Yeh {int(AUTO_DELETE_TIME/60)} minute mein automatic delete ho jayengi."
            unotif = await client.send_message(chat_id=message.chat.id, text=notif_text)
            user_uploaded_videos.append(unotif)
            asyncio.create_task(auto_delete_worker(user_uploaded_videos, AUTO_DELETE_TIME))

        if LOGIN_SYSTEM == True:
            try: await acc.disconnect()
            except: pass                				
        batch_temp.IS_BATCH[message.from_user.id] = True

# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int, user_uploaded_videos: list):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    if CHANNEL_ID:
        try: chat = int(CHANNEL_ID)
        except: chat = message.chat.id
    else: chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    db_caption = await db.get_caption(message.from_user.id)
    caption = db_caption if db_caption else (msg.caption if msg.caption else None)
    dump_channel_id = await db.get_dump_id(message.from_user.id)
    sent_msg = None

    if "Document" == msg_type:
        try: ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except: ph_path = None
        try: sent_msg = await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Video" == msg_type:
        try: ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except: ph_path = None
        try: sent_msg = await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try: sent_msg = await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try: sent_msg = await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try: sent_msg = await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try: ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except: ph_path = None
        try: sent_msg = await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try: sent_msg = await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if sent_msg:
        user_uploaded_videos.append(sent_msg)
        if dump_channel_id:
            try: await sent_msg.copy(chat_id=int(dump_channel_id), caption=caption, parse_mode=enums.ParseMode.HTML)
            except Exception as dump_err: print(f"Instant Dump Sync Failed: {dump_err}")

    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id, [smsg.id])

def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try: msg.document.file_id; return "Document"
    except: pass
    try: msg.video.file_id; return "Video"
    except: pass
    try: msg.animation.file_id; return "Animation"
    except: pass
    try: msg.sticker.file_id; return "Sticker"
    except: pass
    try: msg.voice.file_id; return "Voice"
    except: pass
    try: msg.audio.file_id; return "Audio"
    except: pass
    try: msg.photo.file_id; return "Photo"
    except: pass
    try: msg.text; return "Text"
    except: pass
