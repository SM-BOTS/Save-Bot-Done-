# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import API_ID, API_HASH, ERROR_MESSAGE, LOGIN_SYSTEM, STRING_SESSION, CHANNEL_ID, WAITING_TIME, AUTO_DELETE_TIME
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser

class batch_temp(object):
    IS_BATCH = {}

# Temp dictionary for keeping track of user states (waiting for text input)
USER_STATES = {}

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded:** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


# Auto delete background task worker
async def auto_delete_worker(messages, delay):
    await asyncio.sleep(delay)
    for msg in messages:
        try:
            await msg.delete()
        except:
            pass


# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
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
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"{HELP_TXT}"
    )

# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id, 
        text="**Batch Successfully Cancelled.**"
    )

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
    
    text = (
        "**⚙️ BOT SETTINGS PANEL**\n\n"
        f"📁 **Dump Channel:** {dump_status}\n"
        f"📝 **Custom Caption:** {cap_status}\n\n"
        "Niche diye gaye buttons se apni settings manage karein:"
    )
    
    buttons = [
        [
            InlineKeyboardButton("📁 Set Dump", callback_data="set_dump"),
            InlineKeyboardButton("🗑️ Remove Dump", callback_data="rem_dump")
        ],
        [
            InlineKeyboardButton("📝 Set Caption", callback_data="set_cap"),
            InlineKeyboardButton("🗑️ Remove Caption", callback_data="rem_cap")
        ]
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
        
        text = (
            "**⚙️ BOT SETTINGS PANEL**\n\n"
            f"📁 **Dump Channel:** {dump_status}\n"
            f"📝 **Custom Caption:** {cap_status}\n\n"
            "Niche diye gaye buttons se apni settings manage karein:"
        )
        buttons = [
            [InlineKeyboardButton("📁 Set Dump", callback_data="set_dump"), InlineKeyboardButton("🗑️ Remove Dump", callback_data="rem_dump")],
            [InlineKeyboardButton("📝 Set Caption", callback_data="set_cap"), InlineKeyboardButton("🗑️ Remove Caption", callback_data="rem_cap")]
        ]
        await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "set_dump":
        USER_STATES[user_id] = "waiting_for_dump"
        back_btn = [[InlineKeyboardButton("🔙 Back to Settings", callback_data="open_settings")]]
        await query.message.edit_text(
            "**📁 Apni Private Channel ki ID send karo:**\n\n_(Example: `-1001234567890`)_\n\n⚠️ **Note:** Bot ka channel me Admin hona zaroori hai.",
            reply_markup=InlineKeyboardMarkup(back_btn)
        )
        
    elif data == "rem_dump":
        await db.remove_dump_id(user_id)
        await query.answer("📁 Dump Channel successfully hata diya!", show_alert=True)
        # Refresh Settings
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
        
    elif data == "set_cap":
        USER_STATES[user_id] = "waiting_for_caption"
        back_btn = [[InlineKeyboardButton("🔙 Back to Settings", callback_data="open_settings")]]
        await query.message.edit_text(
            "**📝 Apna naya Custom Caption send karo:**\n\n_Isse purana original caption poora hat jayega aur sirf aapka set kiya hua text dikhega._",
            reply_markup=InlineKeyboardMarkup(back_btn)
        )
        
    elif data == "rem_cap":
        await db.remove_caption(user_id)
        await query.answer("📝 Custom Caption successfully hata diya!", show_alert=True)
        # Refresh Settings
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


# ========================================================
# 💬 INCOMING MESSAGE TEXT & LINKS LOGIC
# ========================================================
@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    user_id = message.from_user.id

    # Check if user is typing setting configuration inputs
    if USER_STATES.get(user_id) == "waiting_for_dump":
        dump_id = message.text.strip()
        if dump_id.startswith("-100"):
            try:
                await db.set_dump_id(user_id, int(dump_id))
                USER_STATES.pop(user_id, None)
                await message.reply_text(f"✅ **Dump Channel ID Successfully Save Ho Gayi:** `{dump_id}`\n\nDobara open karne ke liye `/settings` type karein.")
            except:
                await message.reply_text("❌ **ID Error!** Please make sure you entered numbers properly.")
        else:
            await message.reply_text("❌ **Galat ID!** Channel ID hamesha `-100` se shuru honi chahiye. Dobara try karein ya `/settings` dabaayein.")
        return

    elif USER_STATES.get(user_id) == "waiting_for_caption":
        custom_caption = message.text
        await db.set_caption(user_id, custom_caption)
        USER_STATES.pop(user_id, None)
        await message.reply_text("✅ **Custom Caption Successfully Save Ho Gaya!**\n\nDobara open karne ke liye `/settings` type karein.")
        return

    # Joining chat
    if ("https://t.me/+" in message.text or "https://t.me/joinchat/" in message.text) and LOGIN_SYSTEM == False:
        if TechVJUser is None:
            await client.send_message(message.chat.id, "String Session is not Set", reply_to_message_id=message.id)
            return
        try:
            try:
                await TechVJUser.join_chat(message.text)
            except Exception as e: 
                await client.send_message(message.chat.id, f"Error : {e}", reply_to_message_id=message.id)
                return
            await client.send_message(message.chat.id, "Chat Joined", reply_to_message_id=message.id)
        except UserAlreadyParticipant:
            await client.send_message(message.chat.id, "Chat already Joined", reply_to_message_id=message.id)
        except InviteHashExpired:
            await client.send_message(message.chat.id, "Invalid Link", reply_to_message_id=message.id)
        return
    
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        if LOGIN_SYSTEM == True:
            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                return
            api_id = int(await db.get_api_id(message.from_user.id))
            api_hash = await db.get_api_hash(message.from_user.id)
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=api_hash, api_id=api_id)
                await acc.connect()
            except:
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")
        else:
            if TechVJUser is None:
                await client.send_message(message.chat.id, f"**String Session is not Set**", reply_to_message_id=message.id)
                return
            acc = TechVJUser
				
        batch_temp.IS_BATCH[message.from_user.id] = False
        
        # Track files uploaded to user PM in this specific single/bulk task
        user_uploaded_videos = []
        
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            
            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid, user_uploaded_videos)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid, user_uploaded_videos)
                except Exception as e:
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            
            # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied: 
                    await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    return
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try:    
                        await handle_private(client, acc, message, username, msgid, user_uploaded_videos)               
                    except Exception as e:
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
            await asyncio.sleep(WAITING_TIME)
            
        # ========================================================
        # ⏳ END OF BATCH / SINGLE UPLOAD: NOTIFICATION GENERATOR
        # ========================================================
        if user_uploaded_videos:
            # Send single notification to user PM only
            notif_text = f"⏳ Aapki saari files upload ho gayi hain! Yeh {int(AUTO_DELETE_TIME/60)} minute mein automatic delete ho jayengi."
            unotif = await client.send_message(chat_id=message.chat.id, text=notif_text)
            
            # Add notification message itself to deletion queue
            user_uploaded_videos.append(unotif)
            
            # Start background auto-delete timer for PM videos + notice
            asyncio.create_task(auto_delete_worker(user_uploaded_videos, AUTO_DELETE_TIME))

        if LOGIN_SYSTEM == True:
            try:
                await acc.disconnect()
            except:
                pass                				
        batch_temp.IS_BATCH[message.from_user.id] = True


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int, user_uploaded_videos: list):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    if CHANNEL_ID:
        try:
            chat = int(CHANNEL_ID)
        except:
            chat = message.chat.id
    else:
        chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    # DB Custom Caption Check Logic
    db_caption = await db.get_caption(message.from_user.id)
    if db_caption:
        caption = db_caption  
    else:
        caption = msg.caption if msg.caption else None

    # Get Dump Channel ID from Database (Check if configured)
    dump_channel_id = await db.get_dump_id(message.from_user.id)
            
    # Object holder to store user file info
    sent_msg = None

    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        try:
            sent_msg = await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        try:
            sent_msg = await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            sent_msg = await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            sent_msg = await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            sent_msg = await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None
        try:
            sent_msg = await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            sent_msg = await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True: await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    # 🚀 0 SECOND MIRROR SYSTEM + USER CHOICE VERIFICATION
    if sent_msg:
        user_uploaded_videos.append(sent_msg)
        
        # Agar user ne dump settings me channel save kiya h tabhi execute hoga 
        if dump_channel_id:
            try:
                # Instant forward method using server data copy without uploading again
                await sent_msg.copy(chat_id=int(dump_channel_id), caption=caption, parse_mode=enums.ParseMode.HTML)
            except Exception as dump_err:
                print(f"Instant Dump Sync Failed: {dump_err}")

    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(message.chat.id, [smsg.id])


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass
        

# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01
