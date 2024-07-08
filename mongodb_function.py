from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB连接URI
uri = "mongodb+srv://789william:123Vanoss@cluster0.binj4fs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# 连接MongoDB并选择数据库和集合
def connect_to_mongodb():
    client = MongoClient(uri)
    db = client['MongoClient']  # 数据库名
    collection = db['to_do_list']  # 集合名
    return collection

# 获取用户的所有任务
def get_tasks(user_id):
    try:
        collection = connect_to_mongodb()
        return list(collection.find({'user_id': user_id}))
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        return []

# 更新提醒时间
def update_remind_time(task_id, remind_time):
    try:
        collection = connect_to_mongodb()
        collection.update_one({'_id': task_id}, {'$set': {'remind_time': remind_time}})
    except Exception as e:
        logger.error(f"Error updating remind time: {e}")

# 更新提醒状态
def update_reminded_status(task_id):
    try:
        collection = connect_to_mongodb()
        result = collection.update_one(
            {'_id': ObjectId(task_id)},
            {'$set': {'reminded': True}}  # 更新提醒状态为已提醒
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating reminded status: {e}")
        return False

# 添加新任务
def add_new_task(user_id, task, remind_time):
    try:
        collection = connect_to_mongodb()
        collection.insert_one({
            'user_id': user_id,
            'task': task,
            'remind_time': remind_time,
            'reminded': False,
            'created_at': datetime.now()
        })
    except Exception as e:
        logger.error(f"Error adding new task: {e}")

# 删除任务
def delete_task(task_id):
    try:
        collection = connect_to_mongodb()
        collection.delete_one({'_id': ObjectId(task_id)})
    except Exception as e:
        logger.error(f"Error deleting task: {e}")

# 获取所有任务的数量
def get_task_count():
    try:
        collection = connect_to_mongodb()
        return collection.count_documents({})
    except Exception as e:
        logger.error(f"Error getting task count: {e}")
        return 0

# 获取所有用户的任务
def get_all_tasks():
    try:
        collection = connect_to_mongodb()
        return list(collection.find())
    except Exception as e:
        logger.error(f"Error getting all tasks: {e}")
        return []

# 根据任务ID获取任务详情
def get_task_by_id(task_id):
    try:
        collection = connect_to_mongodb()
        return collection.find_one({'_id': ObjectId(task_id)})
    except Exception as e:
        logger.error(f"Error getting task by ID: {e}")
        return None

# 获取可提醒的任务
def get_remindable_tasks():
    current_time = datetime.now()
    try:
        collection = connect_to_mongodb()
        remindable_tasks = list(collection.find({'remind_time': {'$lte': current_time}, 'reminded': False}))
        logger.info(f"Found {len(remindable_tasks)} remindable tasks.")
        return remindable_tasks
    except Exception as e:
        logger.error(f"Error getting remindable tasks: {e}")
        return []

# 标记任务为已提醒
def mark_task_as_reminded(task_id):
    try:
        collection = connect_to_mongodb()
        collection.update_one({'_id': task_id}, {'$set': {'reminded': True}})
    except Exception as e:
        logger.error(f"Error marking task as reminded: {e}")
