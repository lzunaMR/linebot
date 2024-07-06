from linebot import LineBotApi
from linebot.models import TextSendMessage
from datetime import datetime, timedelta
import logging
import time
import mongodb_function as db

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

line_bot_api = LineBotApi('fqpkaylucHfFHRd3QwkPkjWlF7zKfEF7g7HBg1+uNRJhBtSvRcqnR0lBLDh8mQdG+SWuHy20Aou8/7zoYbB5pe5CPvQCJuK/m98IesmHszsFi4ZG+GvBN7nGezkPe0PtCo6+OhJpR4b9cQTyjGjThQdB04t89/1O/w1cDnyilFU=')

def check_reminders():
    logger.info("Starting reminder checker...")
    while True:
        try:
            logger.info("Checking reminders...")
            remindable_tasks = db.get_remindable_tasks()
            current_time = datetime.now()
            
            for task in remindable_tasks:
                remind_time = task['remind_time']
                if remind_time <= current_time and not task['reminded']:
                    task_id = task['_id']
                    user_id = task['user_id']
                    task_text = task['task']
                    
                    # 发送提醒消息给用户
                    message = TextSendMessage(text=f'记事提醒：{task_text}')
                    line_bot_api.push_message(user_id, messages=message)
                    
                    # 标记任务为已提醒
                    db.mark_task_as_reminded(task_id)
                    
            logger.info("Reminder check complete.")
        
        except Exception as e:
            logger.error(f"Error in reminder checker: {e}")
        
        time.sleep(30)  # 每30秒检查一次

if __name__ == "__main__":
    logger.info("Starting linebot_reminder.py...")
    check_reminders()
