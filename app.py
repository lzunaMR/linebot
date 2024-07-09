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
from keep_render_awake import keep_render_awake

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

line_bot_api = LineBotApi('fqpkaylucHfFHRd3QwkPkjWlF7zKfEF7g7HBg1+uNRJhBtSvRcqnR0lBLDh8mQdG+SWuHy20Aou8/7zoYbB5pe5CPvQCJuK/m98IesmHszsFi4ZG+GvBN7nGezkPe0PtCo6+OhJpR4b9cQTyjGjThQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('6881343d399a45c7cce9b8682c7788cb')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 监视所有来自 /callback 的 Post 请求
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
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f'提醒时间设定为 {remind_time}'))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='无法找到最近记录的事项。'))
    elif event.postback.data.startswith('delete_task&'):
        task_id = event.postback.data.split('&')[1]
        if db.delete_task(task_id):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='已成功删除该记录事项。'))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='删除记录事项时发生错误。请稍后再试。'))

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
                task_at = task['created_at'].strftime('%#m月%-d日')
                # 创建每个旋转木马的列
                carousel_column = CarouselColumn(
                    text=f'{task_text} - {task_at}',
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

def start_reminder_thread():
    reminder_thread = threading.Thread(target=check_reminders)
    reminder_thread.start()
    logger.info("Reminder thread started.")

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
        
        time.sleep(60)  # 每30秒检查一次

if __name__ == "__main__":
    start_reminder_thread()
    
    keep_awake_thread = threading.Thread(target=keep_render_awake)
    keep_awake_thread.daemon = True  # 确保线程在主程序退出时自动结束
    logger.info("Starting keep awake thread...")
    keep_awake_thread.start()
    
    port = int(os.environ.get('PORT', 10000))
    logger.info(f"Running app on port {port}")
    app.run(host='0.0.0.0', port=port)