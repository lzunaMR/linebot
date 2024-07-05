#這些是LINE官方開放的套件組合透過import來套用這個檔案上
from linebot.models import *
import mongodb_function as db
import logging
from datetime import datetime
from bson import ObjectId  # 确保导入ObjectId
logger = logging.getLogger(__name__)
#ImagemapSendMessage(組圖訊息)
def imagemap_message():
    message = ImagemapSendMessage(
        base_url="https://i.imgur.com/BfTFVDN.jpg",
        alt_text='最新的合作廠商有誰呢？',
        base_size=BaseSize(height=2000, width=2000),
        actions=[
            URIImagemapAction(
                #家樂福
                link_uri="https://tw.shop.com/search/%E5%AE%B6%E6%A8%82%E7%A6%8F",
                area=ImagemapArea(
                    x=0, y=0, width=1000, height=1000
                )
            ),
            URIImagemapAction(
                #生活市集
                link_uri="https://tw.shop.com/search/%E7%94%9F%E6%B4%BB%E5%B8%82%E9%9B%86",
                area=ImagemapArea(
                    x=1000, y=0, width=1000, height=1000
                )
            ),
            URIImagemapAction(
                #阿瘦皮鞋
                link_uri="https://tw.shop.com/search/%E9%98%BF%E7%98%A6%E7%9A%AE%E9%9E%8B",
                area=ImagemapArea(
                    x=0, y=1000, width=1000, height=1000
                )
            ),
            URIImagemapAction(
                #塔吉特千層蛋糕
                link_uri="https://tw.shop.com/search/%E5%A1%94%E5%90%89%E7%89%B9",
                area=ImagemapArea(
                    x=1000, y=1000, width=1000, height=500
                )
            ),
            URIImagemapAction(
                #亞尼克生乳捲
                link_uri="https://tw.shop.com/search/%E4%BA%9E%E5%B0%BC%E5%85%8B",
                area=ImagemapArea(
                    x=1000, y=1500, width=1000, height=500
                )
            )
        ]
    )
    return message

#TemplateSendMessage - ButtonsTemplate (按鈕介面訊息)
def buttons_message():
    message = TemplateSendMessage(
        alt_text='好消息來囉～',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="是否要進行抽獎活動？",
            text="輸入生日後即獲得抽獎機會",
            actions=[
                DatetimePickerTemplateAction(
                    label="請選擇生日",
                    data="input_birthday",
                    mode='date',
                    initial='1990-01-01',
                    max='2019-03-10',
                    min='1930-01-01'
                ),
                MessageTemplateAction(
                    label="看抽獎品項",
                    text="有哪些抽獎品項呢？"
                ),
                URITemplateAction(
                    label="免費註冊享回饋",
                    uri="https://tw.shop.com/nbts/create-myaccount.xhtml?returnurl=https%3A%2F%2Ftw.shop.com%2F"
                )
            ]
        )
    )
    return message

#TemplateSendMessage - ConfirmTemplate(確認介面訊息)
def Confirm_Template():

    message = TemplateSendMessage(
        alt_text='是否註冊成為會員？',
        template=ConfirmTemplate(
            text="是否註冊成為會員？",
            actions=[
                PostbackTemplateAction(
                    label="馬上註冊",
                    text="現在、立刻、馬上",
                    data="會員註冊"
                ),
                MessageTemplateAction(
                    label="查詢其他功能",
                    text="查詢其他功能"
                )
            ]
        )
    )
    return message

#旋轉木馬按鈕訊息介面

def Carousel_Template():
    message = TemplateSendMessage(
        alt_text='一則旋轉木馬按鈕訊息',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Number_1_in_green_rounded_square.svg/200px-Number_1_in_green_rounded_square.svg.png',
                    title='這是第一塊模板',
                    text='一個模板可以有三個按鈕',
                    actions=[
                        PostbackTemplateAction(
                            label='回傳一個訊息',
                            data='將這個訊息偷偷回傳給機器人'
                        ),
                        MessageTemplateAction(
                            label='用戶發送訊息',
                            text='我知道這是1'
                        ),
                        URITemplateAction(
                            label='進入1的網頁',
                            uri='https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Number_1_in_green_rounded_square.svg/200px-Number_1_in_green_rounded_square.svg.png'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRuo7n2_HNSFuT3T7Z9PUZmn1SDM6G6-iXfRC3FxdGTj7X1Wr0RzA',
                    title='這是第二塊模板',
                    text='副標題可以自己改',
                    actions=[
                        PostbackTemplateAction(
                            label='回傳一個訊息',
                            data='這是ID=2'
                        ),
                        MessageTemplateAction(
                            label='用戶發送訊息',
                            text='我知道這是2'
                        ),
                        URITemplateAction(
                            label='進入2的網頁',
                            uri='https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Number_2_in_light_blue_rounded_square.svg/200px-Number_2_in_light_blue_rounded_square.svg.png'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Number_3_in_yellow_rounded_square.svg/200px-Number_3_in_yellow_rounded_square.svg.png',
                    title='這是第三個模塊',
                    text='最多可以放十個',
                    actions=[
                        PostbackTemplateAction(
                            label='回傳一個訊息',
                            data='這是ID=3'
                        ),
                        MessageTemplateAction(
                            label='用戶發送訊息',
                            text='我知道這是3'
                        ),
                        URITemplateAction(
                            label='uri2',
                            uri='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Number_3_in_yellow_rounded_square.svg/200px-Number_3_in_yellow_rounded_square.svg.png'
                        )
                    ]
                )
            ]
        )
    )
    return message

#TemplateSendMessage - ImageCarouselTemplate(圖片旋轉木馬)
def image_carousel_message1():
    message = TemplateSendMessage(
        alt_text='圖片旋轉木馬',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/uKYgfVs.jpg",
                    action=URITemplateAction(
                        label="新鮮水果",
                        uri="http://img.juimg.com/tuku/yulantu/110709/222-110F91G31375.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QOcAvjt.jpg",
                    action=URITemplateAction(
                        label="新鮮蔬菜",
                        uri="https://cdn.101mediaimage.com/img/file/1410464751urhp5.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/Np7eFyj.jpg",
                    action=URITemplateAction(
                        label="可愛狗狗",
                        uri="http://imgm.cnmo-img.com.cn/appimg/screenpic/big/674/673928.JPG"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QRIa5Dz.jpg",
                    action=URITemplateAction(
                        label="可愛貓咪",
                        uri="https://m-miya.net/wp-content/uploads/2014/07/0-065-1.min_.jpg"
                    )
                )
            ]
        )
    )
    return message

#===============to do list=============================================

def handle_message(event, line_bot_api):
    user_id = event.source.user_id
    message_text = event.message.text

    logger.info(f"Received message: {message_text}")

    if message_text == '記事情':
        logger.info("Handling '記事情'")
        send_datetime_picker(event, line_bot_api)
    elif message_text == '提醒事項':
        logger.info("Handling '提醒事項'")
        send_to_do_list(event, line_bot_api, user_id)



def send_datetime_picker(event, line_bot_api):
    try:
        logger.info("Sending datetime picker")

        # 假设 task_id 是从数据库中获取的有效 ObjectId
        task_id = str(ObjectId())  # 这里应替换为实际的task_id

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
                                data=f'reminder_time,{task_id}',  # 发送包含 task_id 的 data
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


def send_to_do_list(event, line_bot_api, user_id):
    try:
        logger.info("Sending to-do list")
        tasks = db.get_tasks(user_id)
        contents = []
        for task in tasks:
            task_id = str(task['_id'])
            task_text = f"{task['task']} - {task['remind_time']}"
            contents.append(
                BubbleContainer(
                    body=BoxComponent(
                        layout='vertical',
                        contents=[
                            TextComponent(text=task_text),
                            ButtonComponent(
                                action=DatetimePickerAction(label='修改', data=f'modify,{task_id}', mode='datetime')
                            ),
                            ButtonComponent(
                                action=DatetimePickerAction(label='刪除', data=f'delete,{task_id}', mode='datetime')
                            )
                        ]
                    )
                )
            )
        flex_message = FlexSendMessage(
            alt_text='提醒事項列表',
            contents={
                'type': 'carousel',
                'contents': contents
            }
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    except Exception as e:
        logger.error(f"Error in send_to_do_list: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))

def handle_postback(event, line_bot_api):
    data = event.postback.data

    try:
        if data.startswith('reminder_time'):
            handle_reminder_time(event, line_bot_api, data)
        elif data.startswith('delete'):
            handle_delete(event, line_bot_api, data)
    except Exception as e:
        logger.error(f"Error handling postback: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))

def handle_reminder_time(event, line_bot_api, data):
    try:
        logger.info(f"Received postback data: {data}")

        # 确保 data 中包含两个部分: reminder_time 和 task_id
        if data.count(',') != 1:
            raise ValueError(f"Invalid data format for reminder_time: {data}")

        # 解析数据
        _, task_id = data.split(',', 1)
        
        # 确保 task_id 是有效的 ObjectId
        if not ObjectId.is_valid(task_id):
            raise ValueError(f"Invalid task_id: {task_id}")

        # 从 event.postback.params 中获取 new_time
        new_time = event.postback.params.get('datetime')
        
        if not new_time:
            raise ValueError("New time is not provided in the callback params.")

        logger.info(f"Parsed task_id: {task_id}, new_time: {new_time}")

        # 更新提醒时间
        db.update_remind_time(task_id, new_time)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'提醒時間已更新為：{new_time}')
        )
    except ValueError as ve:
        logger.error(f"ValueError in handle_reminder_time: {ve}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="資料格式錯誤，請稍後再試。"))
    except Exception as e:
        logger.error(f"Error in handle_reminder_time: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))


def handle_delete(event, line_bot_api, data):
    try:
        logger.info(f"Received postback data: {data}")
        task_id = data.split('=')[1]
        db.delete_task(task_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='事項已刪除')
        )
    except Exception as e:
        logger.error(f"Error in handle_delete: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤，請稍後再試。"))
