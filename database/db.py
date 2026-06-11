# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import motor.motor_asyncio
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            session = None,
            api_id = None,
            api_hash = None,
            dump_id = None,      # Naya: Dump Channel ID save karne ke liye
            caption = None       # Naya: Custom Caption save karne ke liye
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('session') if user else None

    async def set_api_id(self, id, api_id):
        await self.col.update_one({'id': int(id)}, {'$set': {'api_id': api_id}})

    async def get_api_id(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('api_id') if user else None

    async def set_api_hash(self, id, api_hash):
        await self.col.update_one({'id': int(id)}, {'$set': {'api_hash': api_hash}})

    async def get_api_hash(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('api_hash') if user else None

    # ========================================================
    # NAYE FUNCTIONS: DUMP CHANNEL & CUSTOM CAPTION KE LIYE
    # ========================================================

    async def set_dump_id(self, id, dump_id):
        """User ki dump channel ID set karne ke liye"""
        await self.col.update_one({'id': int(id)}, {'$set': {'dump_id': dump_id}})

    async def get_dump_id(self, id):
        """User ki dump channel ID check karne ke liye"""
        user = await self.col.find_one({'id': int(id)})
        return user.get('dump_id') if user else None

    async def remove_dump_id(self, id):
        """User ki dump channel ID delete karne ke liye"""
        await self.col.update_one({'id': int(id)}, {'$set': {'dump_id': None}})

    async def set_caption(self, id, caption):
        """User ka custom caption set karne ke liye"""
        await self.col.update_one({'id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        """User ka custom caption check karne ke liye"""
        user = await self.col.find_one({'id': int(id)})
        return user.get('caption') if user else None

    async def remove_caption(self, id):
        """User ka custom caption delete karne ke liye"""
        await self.col.update_one({'id': int(id)}, {'$set': {'caption': None}})

db = Database(DB_URI, DB_NAME if DB_NAME else "TechVJDemoBot")

# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01
