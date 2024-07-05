from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *


#======這裡是呼叫的檔案內容=====
import message as msg_module
from new import *
from Function import *
import mongodb_function as db
#======這裡是呼叫的檔案內容=====

#======python的函數庫==========
from pymongo import MongoClient
from bson import ObjectId
from mongodb_function import get_tasks, update_remind_time, add_new_task
import tempfile, os
from datetime import datetime
import time
import logging
#======python的函數庫==========
#======讓render不會睡著======
"""import threading 
import requests
def wake_up_heroku():
    while 1==1:
        url = 'https://linebot-2os5.onrender.com/' + 'heroku_wake_up'
        res = requests.get(url)
        if res.status_code==200:
            print('喚醒render成功')
        else:
            print('喚醒失敗')
        time.sleep(28*60)

threading.Thread(target=wake_up_heroku).start()"""
#======讓heroku不會睡著======

app = Flask(__name__,static_folder='./static/tmp', static_url_path='/images')
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# 設置日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Channel Access Token
line_bot_api = LineBotApi('GPFEdFRLgM9XvgeoTS16R6c/JJ+RCsAn1DkmU6etLml1g+HE7tPJo02o/7pwr8qZ+SWuHy20Aou8/7zoYbB5pe5CPvQCJuK/m98IesmHsztFfRsKs8vH/NGc+VSR2cjaf+kgUpLXmTvtTEY8wMSYIQdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('6881343d399a45c7cce9b8682c7788cb')

client = MongoClient("mongodb+srv://789william:123Vanoss@cluster0.binj4fs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['MongoClient']
collection = db['to_do_list']

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    user_id = event.source.user_id

    try:
        if '最新合作廠商' in msg:
            message = imagemap_message()
            line_bot_api.reply_message(event.reply_token, message)
        elif '最新活動訊息' in msg:
            message = buttons_message()
            line_bot_api.reply_message(event.reply_token, message)
        elif '註冊會員' in msg:
            message = Confirm_Template()
            line_bot_api.reply_message(event.reply_token, message)
        elif '旋轉木馬' in msg:
            message = Carousel_Template()
            line_bot_api.reply_message(event.reply_token, message)
        elif '圖片畫廊' in msg:
            message = test()
            line_bot_api.reply_message(event.reply_token, message)
        elif '功能列表' in msg:
            message = function_list()
            line_bot_api.reply_message(event.reply_token, message)
        elif '課表' in msg:
            image_path = 'https://github.com/lzunaMR/linebot/blob/master/static/tmp/IMG_2274.jpg?raw=true'
            message = ImageSendMessage(original_content_url=image_path, preview_image_url=image_path)
            line_bot_api.reply_message(event.reply_token, message)
        elif '哈拉' in msg:
            message = TextSendMessage(text='https://pay.halapla.net')
            line_bot_api.reply_message(event.reply_token, message)
        elif '記事情' in msg:
            # Prompt user to enter the task
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請輸入要記的事情：')
            )
            # Update user state to input_task
            collection.update_one(
                {"user_id": user_id},
                {"$set": {"state": "input_task"}},
                upsert=True
            )
        elif '提醒事項' in msg:
            # Retrieve and send all tasks for the user
            tasks = get_tasks(user_id)
            if tasks:
                task_messages = []
                for task in tasks:
                    task_messages.append(TextSendMessage(text=f"事項: {task['task']}, 提醒時間: {task['remind_time']}"))
                line_bot_api.reply_message(event.reply_token, task_messages)
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='沒有提醒事項。'))
        else:
            # Check if user is in input_task state
            user_state = collection.find_one({"user_id": user_id})
            if user_state and user_state.get("state") == "input_task":
                # Save the task
                add_new_task(user_id, msg, None)
                task_id = str(collection.find_one({"user_id": user_id, "task": msg})['_id'])
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='請選擇提醒時間：')
                )
                # Send datetime picker
                send_datetime_picker(event, line_bot_api, task_id)
                # Update user state to choose_reminder_time
                collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"state": "choose_reminder_time"}},
                    upsert=True
                )
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))

# Postback handler for datetime picker
@handler.add(PostbackEvent)
def handle_postback(event):
    try:
        data = event.postback.data
        if data.startswith('reminder_time'):
            handle_reminder_time(event, line_bot_api, data)
    except Exception as e:
        logger.error(f"Error handling postback: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))

# MemberJoinedEvent handler
@handler.add(MemberJoinedEvent)
def welcome(event):
    try:
        uid = event.joined.members[0].user_id
        gid = event.source.group_id
        profile = line_bot_api.get_group_member_profile(gid, uid)
        name = profile.display_name
        message = TextSendMessage(text=f'{name}歡迎加入')
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        logger.error(f"Error welcoming new member: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))

# Function to send datetime picker
def send_datetime_picker(event, line_bot_api, task_id):
    try:
        logger.info("Sending datetime picker")
        flex_message = FlexSendMessage(
            alt_text='選擇提醒時間',
            contents=BubbleContainer(
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(text='請選擇提醒時間：'),
                        ButtonComponent(
                            action=DatetimePickerAction(
                                label='選擇日期時間',
                                data=f'reminder_time,{task_id}',
                                mode='datetime',
                                min=datetime.now().strftime('%Y-%m-%dT%H:%M'),
                                max=None
                            )
                        )
                    ]
                )
            )
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    except Exception as e:
        logger.error(f"Error in send_datetime_picker: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))

# Function to handle reminder time selection
def handle_reminder_time(event, line_bot_api, data):
    try:
        logger.info(f"Received postback data: {data}")
        if data.count(',') != 1:
            raise ValueError(f"Invalid data format for reminder_time: {data}")
        _, task_id = data.split(',', 1)
        if not ObjectId.is_valid(task_id):
            raise ValueError(f"Invalid task_id: {task_id}")
        new_time = event.postback.params.get('datetime')
        if not new_time:
            raise ValueError("New time is not provided in the callback params.")
        logger.info(f"Parsed task_id: {task_id}, new_time: {new_time}")
        update_remind_time(task_id, new_time)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'提醒時間已更新為：{new_time}')
        )
        collection.update_one(
            {"user_id": event.source.user_id},
            {"$set": {"state": "idle"}},
            upsert=True
        )
    except ValueError as ve:
        logger.error(f"ValueError in handle_reminder_time: {ve}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="資料格式錯誤，請稍後再試。"))
    except Exception as e:
        logger.error(f"Error in handle_reminder_time: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)