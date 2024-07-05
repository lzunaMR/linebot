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

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'reminder':
        remind_time = datetime.strptime(event.postback.params['datetime'], '%Y-%m-%dT%H:%M')
        logger.info(f'Reminder time selected: {remind_time}')
        user_id = event.source.user_id
        tasks = db.get_tasks(user_id)
        last_task = tasks[-1] if tasks else None
        if last_task:
            db.update_remind_time(last_task['_id'], remind_time)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'提醒時間設定為 {remind_time}'))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='無法找到最近記錄的事項。'))


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
        tasks = db.get_all_tasks(user_id)
        if tasks:
            task_list = "\n".join([f"{task['_id']}: {task.get('task', '未知任務')}" for task in tasks])
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=task_list))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='沒有找到任何記錄的事項。'))
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