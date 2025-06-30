
import motor.motor_asyncio
from config import HgBotz 

client = motor.motor_asyncio.AsyncIOMotorClient(HgBotz.DB_URL)
db = client[HgBotz.DB_NAME]
chnl_ids = db.chnl_ids
users = db.users

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
                     
