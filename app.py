from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import threading
import os
from datetime import datetime, timedelta
import time
import logging
import message as msg_module
from new import *
from Function import *
import mongodb_function as db

app = Flask(__name__, static_folder='./static/tmp', static_url_path='/images')
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

line_bot_api = LineBotApi('fqpkaylucHfFHRd3QwkPkjWlF7zKfEF7g7HBg1+uNRJhBtSvRcqnR0lBLDh8mQdG+SWuHy20Aou8/7zoYbB5pe5CPvQCJuK/m98IesmHszsFi4ZG+GvBN7nGezkPe0PtCo6+OhJpR4b9cQTyjGjThQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('6881343d399a45c7cce9b8682c7788cb')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 產生用於編輯任務的按鈕
def generate_task_buttons(tasks):
    buttons = []
    for task in tasks:
        button = PostbackAction(
            label=task['task'],
            data=f"edit_task_{task['_id']}"
        )
        buttons.append(button)
    return buttons

# 顯示所有任務的函式
def display_all_tasks(event):
    user_id = event.source.user_id
    tasks = db.get_tasks(user_id)  # 從資料庫取得使用者所有任務
    if tasks:
        task_buttons = generate_task_buttons(tasks)
        message = TemplateSendMessage(
            alt_text='所有任務',
            template=ButtonsTemplate(
                title='所有任務',
                text='請選擇要編輯或刪除的任務：',
                actions=task_buttons
            )
        )
        line_bot_api.reply_message(event.reply_token, message)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='找不到任何任務。'))

# 處理編輯任務細節的功能
@handler.add(PostbackEvent)
def handle_edit_task(event):
    user_id = event.source.user_id
    if event.postback.data.startswith('edit_task_details_'):
        task_id = event.postback.data.split('_')[-1]
        # 實作提示用戶輸入新的任務細節並更新資料庫的邏輯
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入更新後的任務細節。'))

# 處理編輯提醒時間的功能
@handler.add(PostbackEvent)
def handle_edit_reminder_time(event):
    user_id = event.source.user_id
    if event.postback.data.startswith('edit_reminder_time_'):
        task_id = event.postback.data.split('_')[-1]
        # 實作提示用戶選擇新的提醒時間並更新資料庫的邏輯
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請選擇新的提醒時間。'))

# 處理刪除任務的功能
@handler.add(PostbackEvent)
def handle_delete_task(event):
    user_id = event.source.user_id
    if event.postback.data.startswith('delete_task_'):
        task_id = event.postback.data.split('_')[-1]
        db.delete_task(task_id)  # 從資料庫刪除指定任務
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='任務刪除成功。'))

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    user_id = event.source.user_id
    logger.info(f'Received message: {msg} from user: {user_id}')
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
    elif '所有記錄事項' in msg:
        tasks = db.get_tasks(user_id)
        if tasks:
            task_list = "\n".join([f"{task['_id']}: {task['task']}" for task in tasks])
            # Create a carousel template with edit and delete buttons for each task
            carousel_template = CarouselTemplate(columns=[
                CarouselColumn(
                    thumbnail_image_url='https://example.com/task.png',  # Replace with your image URL
                    title='記錄事項',
                    text=task['task'],
                    actions=[
                        PostbackAction(label='編輯', data=f'edit_{task["_id"]}'),
                        PostbackAction(label='刪除', data=f'delete_{task["_id"]}')
                    ]
                ) for task in tasks
            ])
            template_message = TemplateSendMessage(alt_text='所有記錄事項', template=carousel_template)
            line_bot_api.reply_message(event.reply_token, template_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='您目前沒有任何記錄事項。'))

    elif '記錄事項' in msg:
        task = msg.replace('記錄事項', '').strip()
        if task:
            db.add_new_task(user_id, task, None)
            confirm_template = ConfirmTemplate(
                text='紀錄成功！是否需要提醒功能？',
                actions=[
                    MessageAction(label='是', text='是'),
                    MessageAction(label='否', text='否')
                ]
            )
            template_message = TemplateSendMessage(
                alt_text='是否需要提醒功能？', template=confirm_template)
            line_bot_api.reply_message(event.reply_token, template_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入要記錄的事項。'))
    elif msg == '是':
        now = datetime.now()
        datetime_picker_template = TemplateSendMessage(
            alt_text='請選擇提醒時間',
            template=ButtonsTemplate(
                text='請選擇提醒時間',
                actions=[
                    DatetimePickerAction(
                        label="選擇時間",
                        data="reminder",
                        mode="datetime",
                        initial=now.strftime('%Y-%m-%dT%H:%M'),
                        min=now.strftime('%Y-%m-%dT%H:%M'),
                        max=(now + timedelta(days=365)).strftime('%Y-%m-%dT%H:%M')
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, datetime_picker_template)
    elif '提醒時間' in msg:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請使用選擇時間的方式來設定提醒時間。'))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

if __name__ == "__main__":
    reminder_thread = threading.Thread(target=send_reminder_messages)
    reminder_thread.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)