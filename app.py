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
from bson import ObjectId

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
    elif event.postback.data.startswith('delete_task&'):
        task_id = event.postback.data.split('&')[1]
        if db.delete_task(task_id):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已成功刪除該記錄事項。'))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='刪除記錄事項時發生錯誤。請稍後再試。'))

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
            carousel_columns = []
            for task in tasks:
                task_id = task['_id']
                task_text = task['task']
                creation_date = task['formatted_creation_date']
                # 创建每个旋转木马的列
                carousel_column = CarouselColumn(
                    text=f"{task_text}\n建立時間: {creation_date}",
                    actions=[
                        PostbackTemplateAction(
                            label='刪除',
                            data=f'delete_task&{task_id}'  # 使用 PostbackEvent 处理删除操作
                        )
                    ]
                )
                carousel_columns.append(carousel_column)
            
            carousel_template = TemplateSendMessage(
                alt_text='所有記錄事項',
                template=CarouselTemplate(columns=carousel_columns)
            )
            line_bot_api.reply_message(event.reply_token, carousel_template)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='您目前沒有任何記錄事項。'))
        return
    elif '/記' in msg:
        task = msg.replace('/記', '').strip()
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
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

def send_reminder_messages(line_bot_api):
    while True:
        try:
            current_time = datetime.now()
            tasks = db.get_remindable_tasks()
            for task in tasks:
                user_id = task['user_id']
                task_text = task['task']
                line_bot_api.push_message(user_id, TextSendMessage(text=f"提醒: {task_text}"))
                db.mark_task_as_reminded(task['_id'])
        except Exception as e:
            logger.error(f"Error in reminder thread: {e}")
        time.sleep(30)  # 每分鐘檢查一次


if __name__ == "__main__":
    reminder_thread = threading.Thread(target=send_reminder_messages, args=(line_bot_api,))
    reminder_thread.daemon = True  # 設置守護進程
    reminder_thread.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)