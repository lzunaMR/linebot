import schedule
import time
import datetime
import requests
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def keep_render_awake():
    while True:
        current_time = datetime.datetime.now().time()
        if current_time < datetime.time(0, 0) or current_time >= datetime.time(7, 0):
            try:
                response = requests.get("https://linebot-28fd.onrender.com")
                if response.status_code == 200:
                    logger.info("Render is awake")
                else:
                    logger.info("Failed to wake up render")
            except Exception as e:
                logger.error(f"Error while waking up render: {e}")
                time.sleep(60)
        else:
            logger.info("Render is asleep")

        # 等待10分鐘
        time.sleep(10 * 60)

# 開始執行
keep_render_awake()
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)