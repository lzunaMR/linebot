import schedule
import time
import datetime
import requests
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def keep_render_awake():
    current_time = datetime.datetime.now().time()
    if current_time < datetime.time(0, 0) or current_time >= datetime.time(7, 0):
        try:
            response = requests.get("https://linebot-21rc.onrender.com")
            if response.status_code == 200:
                logger.info("Render is awake")
            else:
                logger.info("Failed to wake up render")
        except Exception as e:
            logger.error(f"Error while waking up render: {e}")
    else:
        logger.info("Render is asleep")

# 设置每 10 分钟唤醒一次
schedule.every(10).minutes.do(keep_render_awake)

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logger.info("Starting keep_awake.py...")
    schedule_thread = threading.Thread(target=run_schedule)
    schedule_thread.daemon = True
    schedule_thread.start()
