import motor.motor_asyncio
from config import HgBotz

client = motor.motor_asyncio.AsyncIOMotorClient(HgBotz.DB_URL)
db = client[HgBotz.DB_NAME]
chnl_ids = db.chnl_ids
users = db.users
group_settings = db.group_settings
pm_users_col = db.pm_users



#insert user data
async def insert(user_id):
    user_det = {"_id": user_id}
    try:
        await users.insert_one(user_det)
    except:
        pass
        
# Total User
async def total_user():
    user = await users.count_documents({})
    return user

async def getid():
    all_users = users.find({})
    return all_users

async def delete(id):
    await users.delete_one(id)
                     
async def get_all_users(self):
        return self.users.find({})



# Authorize a chat
async def authorize_chat(chat_id: int):
    await group_settings.update_one({"_id": chat_id}, {"$set": {"auth": True}}, upsert=True)

# Unauthorize a chat
async def unauthorize_chat(chat_id: int):
    await group_settings.delete_one({"_id": chat_id})

# Check if a chat is authorized
async def is_chat_authorized(chat_id: int) -> bool:
    chat = await group_settings.find_one({"_id": chat_id})
    return chat is not None

# Get all authorized chats
async def get_all_authorized_chats():
    return group_settings.find({})

# Add user
async def add_pm_user(user_id: int):
    await pm_users_col.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

# Remove user
async def remove_pm_user(user_id: int):
    await pm_users_col.delete_one({"user_id": user_id})

# List users
async def list_pm_users():
    users = await pm_users_col.find().to_list(length=None)
    return [u["user_id"] for u in users]

# Check if user is allowed
async def is_pm_user(user_id: int) -> bool:
    user = await pm_users_col.find_one({"user_id": user_id})
    return bool(user)
