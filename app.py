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
line_bot_api = LineBotApi('fqpkaylucHfFHRd3QwkPkjWlF7zKfEF7g7HBg1+uNRJhBtSvRcqnR0lBLDh8mQdG+SWuHy20Aou8/7zoYbB5pe5CPvQCJuK/m98IesmHszsFi4ZG+GvBN7nGezkPe0PtCo6+OhJpR4b9cQTyjGjThQdB04t89/1O/w1cDnyilFU=')
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
            message = msg_module.imagemap_message()
            line_bot_api.reply_message(event.reply_token, message)
        elif '最新活動訊息' in msg:
            message = msg_module.buttons_message()
            line_bot_api.reply_message(event.reply_token, message)
        elif '註冊會員' in msg:
            message = msg_module.Confirm_Template()
            line_bot_api.reply_message(event.reply_token, message)
        elif '旋轉木馬' in msg:
            message = msg_module.Carousel_Template()
            line_bot_api.reply_message(event.reply_token, message)
        elif '圖片畫廊' in msg:
            message = msg_module.test()
            line_bot_api.reply_message(event.reply_token, message)
        elif '功能列表' in msg:
            message = msg_module.function_list()
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
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)